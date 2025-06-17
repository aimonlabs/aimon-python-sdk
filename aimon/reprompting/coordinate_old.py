import os
from enum import Enum
from aimon import Detect
from typing import Optional
from dataclasses import dataclass
from telemetry import TelemetryLogger
import time

import random
import string
import logging

## configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


def generate_random_string(length):
  """Generates a random string of letters and digits."""
  characters = string.ascii_letters + string.digits
  return ''.join(random.choice(characters) for i in range(length))


class Framework(Enum):
    LLAMAINDEX = "LlamaIndex"
    LANGCHAIN = "LangChain"
    HAYSTACK = "Haystack"
    NONE = None

@dataclass
class ReactConfig:
    """
    Configuration class for the React configuration settings.

    Attributes:
        publish (bool): Flag indicating whether to publish the results to app.aimon.ai
        max_attempts (int): Maximum number of ReAct attempts
        hallucination_threshold (float): Threshold value to determine hallucination behavior. Defaults to 0.5.
        framework (Optional[Framework]): Optional framework configuration. Defaults to None.
        aimon_api_key (Optional[str]): API key for AIMon integration. If not provided, it attempts to retrieve from environment variable "AIMON_API_KEY".
        model_name (Optional[str]): Name of the model to be used. Defaults to a string based on "aimon-react-model" concatenated with a random string.
        application_name (Optional[str]): Name of the application. Defaults to a string based on "aimon-react-application" concatenated with a random string.

    Methods:
        None
    """
    publish: bool
    max_attempts: int
    ## play around with the threshold to see how it affects the results
    ## hallucination score should be below this threshold to be considered acceptable
    HALLUCINATION_THRESHOLD: float = 0.25
    ## instruction adherence score should be above this threshold to be considered acceptable
    IA_THRESHOLD: float = 0.75
    ## toxicity score should be below this threshold to be considered acceptable
    ## this is a safety filter to prevent toxic outputs and shoudl be set to a low value
    TOXICITY_THRESHOLD: float = 0.25
    framework: Optional[Framework] = None
    aimon_api_key: Optional[str] = os.getenv("AIMON_API_KEY")
    model_name: Optional[str] = "aimon-react-model" + generate_random_string(5)
    application_name: Optional[str] = "aimon-react-application" + generate_random_string(5)

class Coordinator:

    ## Initailze the AIMon Client here
    ## llm_app is outdated for my code but I didn't know how to best call the different LLMs
    def __init__(self, llm_app, react_configuration, context_extractor, reprompter, agent):
        """
        Initializes the Coordinator class.

        Args:
            llm_app: The language model application to be used.
            react_configuration: Configuration settings for the ReAct framework.
            context_extractor: Component responsible for extracting context from input data.
            reprompter: Object used to generate corrective prompts based on feedback.
            agent: The agent responsible for interacting with the language model.
        """
                                                                                   
        self.llm_app = llm_app
        self.context_extractor = context_extractor
        self.react_configuration = react_configuration
        self.reprompter = reprompter
        self.agent = agent
        self.detect = Detect(
            values_returned=['user_query', 'instructions', 'generated_text', 'context'],
            config={
                "instruction_adherence": {
                    "detector_name": "default",
                    "explain": True,
                    "extract_from_system": False
                },
                "hallucination": {
                    "detector_name": "default"
                },
                "toxicity": {
                    "detector_name": "default"
                }
            },
            api_key=self.react_configuration.aimon_api_key,
            ## these are not updated yet
            application_name="reprompter_app",
            model_name="my_model_v1"
        )
        self.telemetry = TelemetryLogger()


    def gen_aimon_instructions(self):
        ## the following can be optimized later to better fit the taxonomy
        ## improve the instructions based on the taxonomy items
        contradiction_ia = [
            "Ensure the response is internally consistent and does not conflict with its own statements."
        ]
        ## is double barrelled a problem? How to deal with when the taxonomy item has multiple related instructions
        ambiguity_ia= [
            "Do not give vague or non-committal answers when the user has asked for a specific response.",
            "Prioritize clarity and precision."
        ]
        ## LengthViolation will need to be extracted from the prompt and is thus not included yet
        ## Hallucination determined separately
        default_instructions =  contradiction_ia + ambiguity_ia
        return default_instructions

    ## Sets up payload dictionary for Coordinator object
    def create_payload(self, context, user_query, user_instructions, generated_text):
        
        default_instructions = self.gen_aimon_instructions()

        aimon_payload = {
            'context':context,
            'user_query':user_query,
            'generated_text':generated_text,
            'instructions':user_instructions + default_instructions,
        }

        aimon_payload['publish'] = self.react_configuration.publish
    
        aimon_payload['config'] = { 'hallucination': {'detector_name': 'default'},
                                    'instruction_adherence': {'detector_name': 'default'},}

        if self.react_configuration.publish:
            aimon_payload['application_name'] = self.react_configuration.application_name
            aimon_payload['model_name'] = self.react_configuration.model_name

        return aimon_payload
    
    ## evaluates the ouput based on instructions, query, and context using the AIMon Detect class
    def detect_aimon_response(self, aimon_payload):
        user_query = aimon_payload['user_query']
        instructions = aimon_payload['instructions']
        response_text = aimon_payload['generated_text']
        context = aimon_payload['context']

        # Decorated inline function with context
        @self.detect
        def run_detection(query, instructions, generated_text, context):
            return query, instructions, generated_text, context

        _, _, _, _, aimon_result = run_detection(user_query, instructions, response_text, context)
        return aimon_result

    ## generates a corrective prompt based on AIMon's feedback
    def gen_reprompt(self, aimon_payload, result):
        return self.reprompter.create_corrective_prompt(result, aimon_payload)

    ## should check for stop conditions like latency, number of iterations
    ## only checks for no voilated instructions for now
    ## returns true if (a) the Feedback Model’s residual error score drops below threshold, (b) a hard cap N iterations is reached, or (c) the global latency budget expires.
    def end_reprom(self, aimon_payload, result, iteration_num):
        ## ends reprompting if the maximum number of iterations is reached
        if iteration_num >= self.react_configuration.max_attempts:
            logger.info(f"Reached maximum number of iterations: {iteration_num}")
            return True
        ## continues reprompting if there is hallucination above a threshold
        if result.detect_response.hallucination["score"] > self.react_configuration.HALLUCINATION_THRESHOLD:
            logger.info("Hallucination. Output needs reprompting.")
            return False
        ## continues reprompting if instruction adherence is too low and below a threshold
        if result.detect_response.instruction_adherence["score"] < self.react_configuration.IA_THRESHOLD:
            logger.info("Instructions not followed. Output needs reprompting.")
            return False
        ## continues reprompting if there are any failed instructions even if the scores are within thresholds
        failed_instructions = self.reprompter.get_failed_instructions(result, aimon_payload)
        if failed_instructions:
            logger.info(f"Failed instructions detected:\n" + "\n".join(failed_instructions))
            return False
        
        ## logs reason for stopping reprompting
        logger.info("Hallucination and instruction adherence scores are within acceptable limits.")
        return True
    
    ## safety / policy filter
    def toxicity_check(self, result):
        if result.detect_response.toxicity["score"] > self.react_configuration.TOXICITY_THRESHOLD:
            logger.warning("Toxicity score is above threshold: {}".format(result.detect_response.toxicity["score"]))
            return True
        return False
    
    ## concatenates the context, user query, and user instructions into a prompt
    def gen_prompt(self, context, user_query, user_instructions):
        default_instructions = self.gen_aimon_instructions()

        prompt = (
            context +
            "\n\nUser Query:\n" + user_query +
            "\n\nUser Instructions:\n" + "\n".join(user_instructions) +
            "\n\nDefault Instructions:\n" + "\n".join(default_instructions)
        )
        return prompt
    
    def get_residual_error_score(self, result):
        """
        Calculate the residual error score based on AIMon response.
        This function should be optimized to return a meaningful score
        that reflects the quality of the response in terms of hallucination and instruction adherence.

        a higher residual error score indicates a worse response
        """
        return result.detect_response.hallucination["score"] + 1 - result.detect_response.instruction_adherence["score"]
    
    # generates a vector of errors and scores for telemetry
    def gen_error_vector(self, result):
        # stores hallucinateion and instruction adherence scores
        scores = {
            "hallucination": result.detect_response.hallucination.get("score", 0.0),
            "instruction_adherence": result.detect_response.instruction_adherence.get("score", 0.0)
        }
        ## stores all failed instructions and the follow probability and explanation
        errors = [
            {
                "type": "instruction_failure",
                "instruction": inst["instruction"],
                "score": inst["follow_probability"],
                "explanation": inst.get("explanation", "")
            }
            for inst in result.detect_response.instruction_adherence.get("instructions_list", [])
            if not inst.get("label", True)
        ]
        # Add hallucination error and top hallucinated sentence to the error vector only if above threshold
        halluc_score = result.detect_response.hallucination.get("score", 0.0)
        hallucinations = result.detect_response.hallucination.get("context_hallucinations", [])

        if halluc_score > self.react_configuration.HALLUCINATION_THRESHOLD:
            if hallucinations:
                top_hallucination = max(hallucinations, key=lambda h: h["score"])
                errors.append({
                    "type": "hallucination",
                    "score": halluc_score,
                    "text": top_hallucination["text"],
                    "sentence_score": top_hallucination["score"]
                })
            else:
                logger.warning("Hallucination score is above threshold, but no hallucinations were found.")
        return scores, errors
    
    def coordinate(self, llm_num, context, user_query, user_instructions):
        ## store a map is the llm output map to the residual error score to output the best response
        iteration_outputs = {}  # key: iteration number, value: dict with output and error

        start = time.time()

        # Initial prompt and response
        curr_prompt = self.gen_prompt(context, user_query, user_instructions)
        ## call llm
        curr_generated_text = self.agent.get_response(llm_num, curr_prompt)

        logger.info("=== Prompt ===")
        logger.info(curr_prompt)
        logger.info("\n=== Generated Response ===")
        logger.info(curr_generated_text)

        # Create AIMon payload and detect response
        curr_payload = self.create_payload(context, user_query, user_instructions, curr_generated_text)
        ## evaluate response on hallucination, instruction adherence, and toxicity
        curr_result = self.detect_aimon_response(curr_payload)

        latency_ms = (time.time() - start) * 1000

        # Placeholder for token counts (update if available)
        prompt_tokens = 0
        response_tokens = 0

        # Initialize iteration variables
        iteration_num = 1

        # Calculate residual error score
        residual_error = self.get_residual_error_score(curr_result)

        # Store all telemetry per iteration
        telemetry_data = []
        # Scores and errors for telemetry
        scores, errors = self.gen_error_vector(curr_result)

        # checks for toxicity to act as safety filter
        if self.toxicity_check(curr_result):
            logger.warning("Toxicity check failed. Aborting further processing.")
            telemetry_entry = {
                "iteration": iteration_num,
                "latency_ms": latency_ms,
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens,
                "scores": scores,
                "error_vector": errors,
                "residual_error": residual_error,
                "stop_reason": "toxic",
                "prompt": curr_prompt,
                "response_text": curr_generated_text
            }
            telemetry_data.append(telemetry_entry)
            self.telemetry.emit(**telemetry_entry)
            return

        ## update map with current iteration
        iteration_outputs[iteration_num] = {
            "response_text": curr_generated_text,
            "residual_error_score": residual_error
        }

        while not self.end_reprom(curr_payload, curr_result, iteration_num):

            ## emit telemetry information
            telemetry_entry = {
                "iteration": iteration_num,
                "latency_ms": latency_ms,
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens,
                "scores": scores,
                "error_vector": errors,
                "residual_error": residual_error,
                "stop_reason": "continue",
                "prompt": curr_prompt,
                "response_text": curr_generated_text
            }
            telemetry_data.append(telemetry_entry)
            self.telemetry.emit(**telemetry_entry)
            logger.info(f"Iteration Num = {iteration_num}")
            # Track latency per iteration
            start = time.time()

            # Generate corrective prompt
            curr_prompt = self.gen_reprompt(curr_payload, curr_result)
            logger.info("=== Corrective Prompt ===")
            logger.info(curr_prompt)
            # retrieve new response from LLM to the corrective prompt
            curr_generated_text = self.agent.get_response(llm_num, curr_prompt)
            logger.info("\n=== Generated Response ===")
            logger.info(curr_generated_text)

            # updating latency
            latency_ms = (time.time() - start) * 1000  # update per iteration

            # Create new AIMon payload with the updated prompt and response
            # Note: This assumes the context remains the same throughout iterations
            curr_payload = self.create_payload(context, user_query, user_instructions, curr_generated_text)

            ## evaluates the new response on hallucination, instruction adherence, and toxicity
            curr_result = self.detect_aimon_response(curr_payload)

            # Real token counts if available
            prompt_tokens = 0  # replace with: self.token_counter.get_prompt_tokens(curr_prompt)
            response_tokens = 0  # replace with: self.token_counter.get_response_tokens(curr_generated_text)

            # creates score and error vectors for the current result to store in telemetry
            scores, errors = self.gen_error_vector(curr_result)

            # increments iteration
            iteration_num += 1

            # calculate residual error score for the current result
            residual_error = self.get_residual_error_score(curr_result)
            iteration_outputs[iteration_num] = {
                "response_text": curr_generated_text,
                "residual_error_score": residual_error
            }

        # Emit telemetry for the final iteration (stop condition)
        telemetry_entry = {
            "iteration": iteration_num,
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "scores": scores,
            "error_vector": errors,
            "residual_error": self.get_residual_error_score(curr_result),
            "stop_reason": "stop",
            "prompt": curr_prompt,
            "response_text": curr_generated_text
        }
        telemetry_data.append(telemetry_entry)
        self.telemetry.emit(**telemetry_entry)

        # retrieving the iteration with the lowest residual error score from the iteration_outputs map
        if not iteration_outputs:
            logger.error("No iterations were performed. Unable to determine the best output.")
            return None  # Or handle this case as per your application's requirements

        best_iteration = min(iteration_outputs.values(), key=lambda x: x["residual_error_score"])
        best_output = best_iteration["response_text"]
        best_residual_error = best_iteration["residual_error_score"]


        print("Telemetry data for all iterations:")
        print(telemetry_data)
        print("\nFinal Output:")
        print(best_output)
        print(f"Residual Error Score: {best_residual_error}")
        print(f"Latency (ms): {latency_ms}")
        print(f"Total Iterations: {iteration_num}")

        return telemetry_data