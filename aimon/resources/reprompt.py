
## Static Systemp Prompt
static_system_prompt = "    Please generate a new response, and take into consideration the following factors:\
                            1. If the hallucination score is between 0 and 0.5, no special action is required for improving accuracy.\
                            2. If the hallucination score is between 0.5 and 0.75, please focus on reducing any noticeable inaccuracies, while ensuring the response is as reliable as possible.\
                            3. If the hallucination score is between 0.75 and 1, take extra care to minimize significant inaccuracies and ensure that the response is mostly factual and reliable, avoiding any fictional or misleading content.\
                            4. Please make sure to follow the instructions properly, which were not complied with earlier. Also, ensure that all the instructions provided are properly followed.\
                        "


## The Re-Prompting Function
def llm_reprompting_function(user_query, 
                             user_instructions, 
                             llm_response, 
                             aimon_response, 
                             detect,                            # detect object configured by the user using AIMon Detect
                             extract_response_metadata,         # Function to retrieve context from the LLM response
                             conservative_llm,                  # Custom LLM, specified by the user. To be employed for reprompting.
                             get_response,                      # Function to get LLM response for a given query.
                             reprompting_frequency=2,
                             hallucination_threshold=0.75):

    ## Decorating the `extract_response_metadata` function with `detect`
    extract_response_metadata = detect(extract_response_metadata)

    for _ in range(reprompting_frequency):

        failed_instructions = []

        ## Loop to check for failed instructions
        for x in aimon_response.detect_response.instruction_adherence['results']:
            if x['adherence'] == False:
                failed_instructions.append(x['instruction'])

        if hallucination_threshold > 0 and (aimon_response.detect_response.hallucination['score'] >= hallucination_threshold or len(failed_instructions)>0):
            
            new_response = get_response(user_query, conservative_llm)
            
            context, user_query, user_instructions, llm_response, aimon_response = extract_response_metadata(user_query, user_instructions, new_response)

        else:
            break
    
    return llm_response, aimon_response