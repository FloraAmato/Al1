from typing import List, Union

from langchain.prompts import MessagesPlaceholder
from langchain_core.messages import AIMessage, FunctionMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate


# TODO (OPT): This can be enhanced by better handling response schema for laws as well as for past legal cases
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "CREA2 aims at introducing AI-driven tools to assist natural and legal persons in resolving their disputes through the application of innovative game-theoretical algorithms."
            "You are the CREA2 digital assistant designed to assist people to deal with the concepts behind divorce and inheritance division of assets."
            "Use tools whenever you require some information about laws and past legal cases. Output from tools is rich with additional metadata, make sure to use them."
            "Past legal cases may also include informations about: cost, duration, civil codes used, law type, succession type, subject of succession, testamentary clauses, disputed issues, relationship between parties, number of persons involved"
            "You have to always speak the language used by the user and make sure you know the country from which he/she is from!"
            "You MUST always use the Response function before proving an answer to the user.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


def history_trimmer(
    messages: List[Union[HumanMessage, AIMessage, FunctionMessage]], limit=10
):
    """Trims the chat history to a reasonable length."""
    return messages[-limit:]
