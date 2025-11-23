from langchain.agents.format_scratchpad import format_to_openai_function_messages


def create_agent(prompt, llm_with_functions, parse_output_schema):
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_functions
        | parse_output_schema
    )
    return agent
