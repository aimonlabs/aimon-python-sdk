from aimon import Client
from typing import Optional
from dataclasses import dataclass

@dataclass
class ReactConfig:
    publish: bool
    max_attempts: int
    aimon_api_key: str
    hallucination_threshold: float
    framework: Optional[str] = None
    model_name: Optional[str] = "aimon-react-model"
    application_name: Optional[str] = "aimon-react-application"

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
    def react(self, user_query, user_instructions,):

        llm_response = self.llm_app(user_query, user_instructions, reprompted_flag=False)
        
        context = self.context_extractor(user_query, user_instructions, llm_response)    

        ## Generated text for LLM Response, if the user employs the LlamaIndex framework
        if llm_response.response or self.react_configuration.framework=="llamaindex":
            generated_text = llm_response.response
        else:
            generated_text = llm_response
    
        aimon_payload = self.create_payload(context, user_query, user_instructions, generated_text)
    
        detect_response = self.detect_aimon_response(aimon_payload)

        for _ in range(self.react_configuration.max_attempts):

            failed_instructions = []
            ## Loop to check for failed instructions
            for x in detect_response.instruction_adherence['results']:
                if x['adherence'] == False:
                    failed_instructions.append(x['instruction'])

            hallucination_score = detect_response.hallucination['score'] 

            ## Check whether the hallucination score is greater than the required threshold OR if any of the supplied instructions are not complied with
            if  self.react_configuration.hallucination_threshold > 0 and \
                (hallucination_score > self.react_configuration.hallucination_threshold or len(failed_instructions)>0): 
                
                llm_response = self.llm_app(user_query, user_instructions, reprompted_flag=True, hallucination_score=hallucination_score)
                
                context = self.context_extractor(user_query, user_instructions, llm_response)
                
                ## Generated text for LLM Response, if the user employs the LlamaIndex framework
                if llm_response.response or self.react_configuration.framework=="llamaindex":
                    generated_text = llm_response.response
                else:
                    generated_text = llm_response

                new_aimon_payload = self.create_payload(context, user_query, user_instructions, generated_text)

                detect_response = self.detect_aimon_response(new_aimon_payload)


        if hallucination_score > self.react_configuration.hallucination_threshold:
            return f"The generated LLM response, even after {self.react_configuration.max_attempts} attempts of ReAct is still hallucinated. The response: {generated_text}"

        return generated_text