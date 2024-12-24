from aimon import Detect
from dataclasses import dataclass

@dataclass
class ReactConfig:
    publish: bool
    model_name: str
    max_attempts: int
    aimon_api_key: str
    application_name: str
    values_returned: list[str]
    hallucination_threshold: float
    aimon_config: dict[str, dict[str, str]]

## ReAct -> Reason and Act

def react(  llm_app,
            user_query,
            user_instructions,
            context_extractor,
            react_configuration,
        ):
    
    detect = Detect(values_returned = react_configuration.values_returned,
                    api_key = react_configuration.aimon_api_key,
                    config = react_configuration.aimon_config,
                    publish = react_configuration.publish,
                    application_name = react_configuration.application_name,
                    model_name = react_configuration.model_name,
                )

    llm_response = llm_app(user_query, user_instructions, reprompted_flag=False)

    ## Decorating the context_extractor function with AIMon's "detect"
    context_extractor = detect(context_extractor)
    
    _, _, _, query_result, aimon_response = context_extractor(user_query, user_instructions, llm_response)

    for _ in range(react_configuration.max_attempts):

        failed_instructions = []
        ## Loop to check for failed instructions
        for x in aimon_response.detect_response.instruction_adherence['results']:
            if x['adherence'] == False:
                failed_instructions.append(x['instruction'])

        ## Check whether the hallucination score is greater than the required threshold OR if any of the supplied instructions are not complied with
        if  react_configuration.hallucination_threshold > 0 and \
            (aimon_response.detect_response.hallucination['score'] > react_configuration.hallucination_threshold or len(failed_instructions)>0): 
            
            llm_response = llm_app(user_query, user_instructions, reprompted_flag=True)

            _, _, _, query_result, aimon_response = context_extractor(user_query, user_instructions, llm_response)

    return query_result




## llm_app is a function that has both conservative and creative LLMs to its access
## returns the LLM's response to the user's query

## Template for llm_app function
# def llm_app(user_query, user_instructions, reprompted_flag=False):
#     from aimon_llamaindex import get_response
#     if reprompted_flag==False:
#         return get_response(user_query, retriever, llm_creative)
#     else:
#         llm_conservative.system_prompt += user_instructions
#         return get_response(user_query, retriever, llm_conservative)