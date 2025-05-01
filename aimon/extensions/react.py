import os
from enum import Enum
from aimon import Client
from typing import Optional
from dataclasses import dataclass

import random
import string

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
    hallucination_threshold: float = 0.5
    framework: Optional[Framework] = None
    aimon_api_key: Optional[str] = os.getenv("AIMON_API_KEY")
    model_name: Optional[str] = "aimon-react-model" + generate_random_string(5)
    application_name: Optional[str] = "aimon-react-application" + generate_random_string(5)

class React:
    
    ## Initailze the AIMon Client here
    def __init__(self, llm_app, react_configuration, context_extractor):
                                                                                   
        self.llm_app = llm_app
        self.context_extractor = context_extractor
        self.react_configuration = react_configuration
        self.client = Client(auth_header="Bearer {}".format(self.react_configuration.aimon_api_key))

    def create_payload(self, context, user_query, user_instructions, generated_text):
        
        aimon_payload = {
            'context':context,
            'user_query':user_query,
            'generated_text':generated_text,
            'instructions':user_instructions,
        }

        aimon_payload['publish'] = self.react_configuration.publish
        aimon_payload['config'] = { 'hallucination': {'detector_name': 'default'},
                                    'instruction_adherence': {'detector_name': 'default'},}

        if self.react_configuration.publish:
            aimon_payload['application_name'] = self.react_configuration.application_name
            aimon_payload['model_name'] = self.react_configuration.model_name

        return aimon_payload

    def detect_aimon_response(self,aimon_payload):
        
        try:
            detect_response = self.client.inference.detect(body=[aimon_payload])
            # Check if the response is a list
            if isinstance(detect_response, list) and len(detect_response) > 0:
                detect_result = detect_response[0]
            elif isinstance(detect_response, dict):
                detect_result = detect_response  # Single dict response
            else:
                raise ValueError("Unexpected response format from detect API: {}".format(detect_response))
        except Exception as e:
                # Log the error and raise it
                print(f"Error during detection: {e}")
                raise
        
        return detect_result

    ## ReAct -> Reason and Act
    def react(self, user_query, user_instructions):
        """
        AIMon-ReAct -> Reason and Act with AIMon

        where ReAct score: 
                            1.0     if after n attempts of ReAct, the LLM follows instructions and generates a non hallucinated response.
                            0.5     if after n attempts of ReAct, either the LLM response follows user_instructions or is under hallucination threshold [BUT NOT BOTH]. 
                            0.0     otherwise.
        """
        result = {
            'responses':             [],
            'hallucination_scores':  [],
            'adherence':             [],                
            'react_score':           0.0     ## 0.0 by assumption
        }

        llm_response = self.llm_app(user_query, user_instructions, reprompted_flag=False)

        context = self.context_extractor(user_query, user_instructions, llm_response)    

        if isinstance(llm_response, str):
            generated_text = llm_response
        elif self.react_configuration.framework.value=="LlamaIndex" or hasattr(llm_response, 'response'):
            generated_text = llm_response.response
        else:
            generated_text = llm_response
    
        aimon_payload = self.create_payload(context, user_query, user_instructions, generated_text)
    
        detect_response = self.detect_aimon_response(aimon_payload)
        
        hallucination_score = detect_response.hallucination['score'] 

        failed_instruction_counter = 0
        ia_feedback = ""
        ## Loop to check for failed instructions
        for x in detect_response.instruction_adherence['results']:
            if x['adherence'] == False:
                failed_instruction_counter+=1
                adherence = False
                ia_feedback += f"For the instruction {x['instruction']}, the adherence detector evaluated that {x['detailed_explanation']}."
        if failed_instruction_counter == 0:
            adherence = True
        if ia_feedback=="":
            ia_feedback="All the instructions were complied with."
        ## Baseline
        result['adherence'].append(adherence)
        result['responses'].append(generated_text)
        result['hallucination_scores'].append(hallucination_score)
        
        for _ in range(self.react_configuration.max_attempts):

            ## Check whether the hallucination score is greater than the required threshold OR if any of the supplied instructions are not complied with
            if  self.react_configuration.hallucination_threshold > 0 and \
                (hallucination_score > self.react_configuration.hallucination_threshold or failed_instruction_counter>0): 
                
                llm_response = self.llm_app(user_query, 
                                            user_instructions, 
                                            reprompted_flag=True, 
                                            last_llm_response = generated_text, 
                                            hallucination_score=hallucination_score, 
                                            ia_feedback = ia_feedback)
                
                context = self.context_extractor(user_query, user_instructions, llm_response)
                
                ## Generated text for LLM Response, if the user employs the LlamaIndex framework
                if self.react_configuration.framework.value=="LlamaIndex" or llm_response.response:
                    generated_text = llm_response.response
                else:
                    generated_text = llm_response

                new_aimon_payload = self.create_payload(context, user_query, user_instructions, generated_text)

                detect_response = self.detect_aimon_response(new_aimon_payload)

                hallucination_score = detect_response.hallucination['score'] 

                ia_feedback = ""
                failed_instruction_counter = 0

                for x in detect_response.instruction_adherence['results']:
                    if x['adherence'] == False:
                        failed_instruction_counter+=1
                        adherence = False
                        ia_feedback += f"For the instruction {x['instruction']}, the adherence detector evaluated that {x['detailed_explanation']}."
                if failed_instruction_counter == 0:
                    adherence = True
                if ia_feedback=="":
                    ia_feedback="All the instructions were complied with."
            
                result['adherence'].append(adherence)
                result['responses'].append(generated_text)
                result['hallucination_scores'].append(hallucination_score)
            
            else:
                break
        
        ## The hallucination score and adherence here are from the last attempt of the max attempts
        if hallucination_score > self.react_configuration.hallucination_threshold and adherence==False:
            # result['responses'].append(f"Even after {self.react_configuration.max_attempts} attempts of AIMon react, the LLM neither adheres to the user instructions, nor generates a response that is not hallucinated. Final LLM response: {generated_text}")
            # result['hallucination_scores'].append(hallucination_score)
            result['react_score']=0.0
        elif hallucination_score > self.react_configuration.hallucination_threshold and adherence==True:
            # result['responses'].append(f"Although the LLM adheres to the user instructions, the generated response, even after {self.react_configuration.max_attempts} attempts of AIMon ReAct is still hallucinated. Final LLM response: {generated_text}")
            # result['hallucination_scores'].append(hallucination_score)
            result['react_score']=0.5
        elif hallucination_score <= self.react_configuration.hallucination_threshold and adherence==False:
            # result['responses'].append(f"Although the LLM generates a non-hallucinated response, it fails to adhere to the user instructions, even after {self.react_configuration.max_attempts} attempts of AIMon ReAct. Final LLM response: {generated_text}")
            # result['hallucination_scores'].append(hallucination_score)
            result['react_score']=0.5
        else:
            # result['responses'].append(f"This response is below the hallucination threshold and adheres to the user instructions. Response {generated_text}")
            # result['hallucination_scores'].append(hallucination_score)
            result['react_score']=1.0

        return result