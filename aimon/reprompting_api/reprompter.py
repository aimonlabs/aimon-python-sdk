from aimon.reprompting_api.utils import get_failed_instructions_count, get_failed_instructions, get_failed_toxicity_instructions
from string import Template
import logging

logger = logging.getLogger(__name__)

class Reprompter:     
    """
    Generates a template for corrective reprompting for improving LLM responses
    based on AIMon evaluation results. This class combines failed instruction
    feedback and background information to trigger iterative
    improvement prompts for stateless LLMs.
    The template is designed to accept substitutions for system_prompt, user_query, and context.

    Designed for use in open-source contexts where developers may want to
    customize the prompt structure or language.
    """                                                       

    def create_corrective_prompt(self, result, aimon_payload: dict) -> Template:
        """
        Build a corrective prompt **template** for the next LLM response.

        Placeholders:
            {system_prompt} – The original system prompt
            {user_query} – The user query
            {context} – The context string

        Args:
            result: AIMon detection result object.
            aimon_payload (dict): Original payload containing:
                - 'system_prompt' (str)
                - 'user_query' (str)
                - 'context' (str)
                - 'generated_text' (str)
                - 'instructions' (list[str])

        Returns:
            Template: A string.Template object (with placeholders for substitution).
        """
        try:
            failed_instructions = get_failed_instructions(result)
            failed_count = get_failed_instructions_count(result)
            logger.debug(f"Failed instructions ({failed_count}): {failed_instructions}")

            tone = self.determine_tone(failed_count)
            toxicity_feedback = self.get_toxicity_reprompt(result)
            failed_instructions_reprompt = self.format_failed_instructions(failed_instructions, toxicity_feedback)
            passed_instructions = self.format_passed_instructions(self.get_passed_instructions(result, aimon_payload))
            generated_text = aimon_payload.get('generated_text', '')

            # Build template string (placeholders for substitution)
            template_str = (
                "Original system prompt:\n"
                "${system_prompt}\n\n"
                "Revise your previous response to this query:\n"
                "${user_query}\n\n"
                "Context:\n"
                "${context}\n\n"
                "Previous response:\n"
                f"{generated_text}\n\n"
                f"{tone}\n\n"
                f"{failed_instructions_reprompt}\n\n"
                "Preserve correct content. Return only the revised output with no extra explanation.\n"
                f"{passed_instructions}\n"
            )
            logger.debug(f"Generated corrective prompt template:\n{template_str}")
            return Template(template_str)
        except Exception as e:
            logger.error(f"Error generating corrective prompt: {e}")
            raise RuntimeError(
                f"Corrective prompt template generation failed: {type(e).__name__} — {e}"
            ) from e

    def get_toxicity_reprompt(self, result) -> str:
        """
        Generate feedback for detected toxicity failures in the following format:
            Your reply contained toxic content. Remove any harmful, abusive, or unsafe language.
            1. We are X% confident that your response had the following issue:
            → Violation: "..."
            → Explanation: "..."

        Args:
            result: AIMon detection result.

        Returns:
            str: Toxicity-specific feedback, or None if no toxicity detected.
        """
        try:
            failed_instructions = get_failed_toxicity_instructions(result)
            if not failed_instructions:
                return ""
            logger.info(f"Toxicity violations detected: {len(failed_instructions)}")
            lines = ["Your reply contained toxic content. Remove any harmful, abusive, or unsafe language."]
            for i, failed_instruction in enumerate(failed_instructions, start=1):
                confidence = failed_instruction.get("score", 0.0) * 100
                confidence_str = f"{confidence:.2f}%"
                lines.append(
                    f"{i}. We are {confidence_str} confident that your response had the following issue:\n"
                    f"→ Violation: \"{failed_instruction.get('instruction', '[Unknown]')}\"\n"
                    f"→ Explanation: {failed_instruction.get('explanation', '[No explanation provided]')}\n"
                )
            return "\n\n".join(lines)
        except Exception as e:
            logger.error(f"Error generating toxicity feedback: {e}")
            return ""
        
    def get_reprompt_per_instruction(self, failed_instruction):
        """
        Corrective feedback for a single failed instruction in the following format:
            1. We are X% confident that the following instruction was not followed:
            → Violated Instruction: "..."
            → Explanation: "..."

        Args:
            failed_instruction (dict): Failed instruction data containing:
                - 'instruction' (str)
                - 'score' (float)
                - 'explanation' (str)

        Returns:
            str: Formatted feedback for the failed instruction.
        """       
        try:
            confidence = (1.0 - failed_instruction.get("score", 0.0)) * 100
            confidence_str = f"{confidence:.2f}%"
            return (
                f" We are {confidence_str} confident that the following instruction was not followed:\n"
                f"→ Violated Instruction: \"{failed_instruction.get('instruction', '[Unknown]')}\"\n"
                f"→ Explanation: {failed_instruction.get('explanation', '[No explanation provided]')}\n"
            )
        except Exception as e:
            logger.error(f"Error formatting failed instruction: {e}")
            raise RuntimeError(
                f"Corrective prompt generation failed: Unexpected error of type {type(e).__name__} — {e}"
            ) from e
        
    def format_failed_instructions(self, failed_instructions, toxicity_feedback: str = None):
        """
        Combine toxicity feedback with general failed instructions into a formatted block.

        Args:
            failed_instructions (list): List of failed instruction dictionaries.
            toxicity_feedback (str, optional): Pre-generated toxicity feedback block.

        Returns:
            str: Combined formatted feedback string.
        """
        lines = []
        if toxicity_feedback:
            lines.append(toxicity_feedback)
        if failed_instructions:
            lines.append("Fix the following:")
            for i, error in enumerate(failed_instructions, start=1):
                lines.append(f"{i}. {self.get_reprompt_per_instruction(error)}")
        if not lines:
            return "No major issues."
        return "\n\n".join(lines)

    def get_passed_instructions(self, result, aimon_payload):
        """
        Retrieve instructions that passed all adherence and groundedness checks.

        Args:
            result: AIMon detection result.
            aimon_payload (dict): Original payload containing the full instruction list.

        Returns:
            list: Passed instruction strings.
        """
        try:
            all_instructions = aimon_payload.get("instructions", [])
            failed_instructions = {item["instruction"] for item in get_failed_instructions(result)}
            return [instr for instr in all_instructions if instr not in failed_instructions]
        except Exception as e:
            logger.error(f"Error determining passed instructions: {e}")
            return []
        
    def format_passed_instructions(self, passed_instructions) -> str:
        """
        Format passed instructions to reinforce adherence in the next iteration.

        Args:
            passed_instructions (list): Passed instruction strings.

        Returns:
            str: Formatted reminder block for passed instructions.
        """
        if not passed_instructions:
            return ""
        return (
            "You did well on these instructions. It is important that you continue to follow these instructions:\n" +
            "\n".join(f"- {instr}" for instr in passed_instructions)
        )

    def determine_tone(self, failed_count: int) -> str:
        """
        Decide the corrective prompt tone based on failure severity:
        
            if failed instructions >= 3: 
                    Your reply had major issues. Fix all points below.
            if failed instructions between 2 and 3:
                    Some parts were off. Improve using the notes below.
            if less than 2:
                    Almost there! Just a few small fixes needed.

        Args:
            failed_count (int): Total number of failed instructions.

        Returns:
            str: Tone-setting string for the corrective prompt.
        """
        if failed_count >= 3:
            return "Your reply had major issues. Fix all points below."
        elif failed_count >= 2:
            return "Some parts were off. Improve using the notes below."
        else:
            return "Almost there. Just a few small fixes needed."

