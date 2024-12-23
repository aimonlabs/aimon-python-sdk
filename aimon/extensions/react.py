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

    llm_response = llm_app(user_query, reprompted_flag=False)

    ## Decorating the context_extractor function with AIMon's "detect"
    context_extractor = detect(context_extractor)
    
    _, _, _, query_result, aimon_response = context_extractor(user_query, user_instructions, llm_response)

    for _ in range(react_configuration.max_attempts):

        if aimon_response.detect_response.hallucination['score'] > react_configuration.hallucination_threshold: 
            llm_response = llm_app(user_query, reprompted_flag=True)
            _, _, _, query_result, aimon_response = context_extractor(user_query, user_instructions, llm_response)

    return query_result


## To do:
## Add instruction adherence logic in the next iteration


## llm_app is a function that has both conservative and creative LLMs to its access
## returns the LLM's response to the user's query

## Template for llm_app function
# def llm_app(user_query, reprompted_flag=False):
#     creative_llm: function
#     conservative_llm: function
#     if reprompted_flag==False:
#         return creative_llm.query(user_query)
#     else:
#         return conservative_llm.query(user_query)