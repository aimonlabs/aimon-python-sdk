class Reprompter:                                                            

    def get_failed_instructions(self, result, aimon_payload):
        ia_failures = result.detect_response.instruction_adherence.get("instructions_list", [])
        groundedness_failures = result.detect_response.groundedness.get("instructions_list", [])

        failed_instructions = []

        for item in ia_failures:
            if not item.get("label", True):
                failed_instructions.append(f'- "{item["instruction"]}" because {item["explanation"]} (from instruction_adherence)')

        for item in groundedness_failures:
            if not item.get("label", True):
                failed_instructions.append(f'- "{item["instruction"]}" because {item["explanation"]} (from groundedness)')

        return failed_instructions

    def create_corrective_prompt(self, result, aimon_payload):
        
        #hallucinated_sentences = self.get_hallucinated_sentences(result)

        # Extract failed instructions with explanations
        failed_instructions = self.get_failed_instructions(result, aimon_payload)

        # Build issue summary
        issue_lines = []

        """
        if hallucinated_sentences:
            issue_lines.append("The following sentence may be hallucinated:")
            issue_lines.extend(hallucinated_sentences)
        """
        if failed_instructions:
            issue_lines.append("The response also violates these instructions:")
            issue_lines.extend(failed_instructions)
    
        issue_text = "\n".join(issue_lines) if issue_lines else "No major issues were detected."

        # Compose final LLM prompt
        prompt = (
            "You are revising your previous response to this query:\n"
            f"{aimon_payload['user_query']}\n\n"
            ## Include the original response for context
            "Issues detected in your response:\n"
            f"{issue_text}\n\n"
            "Please revise your response to fix the problems listed above. Follow all original instructions carefully.\n"
            "Keep the correct content. Do not explain or comment. Just return the improved response."
        )

        return prompt

