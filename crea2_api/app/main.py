import os
import logging
from fastapi import FastAPI, HTTPException
from langchain.agents import AgentExecutor
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.agent import create_agent
from src.chroma import get_chroma_client, upload_documents_to_chroma
from src.output_parser import parse_output_schema, parse_sources
from src.prompt import prompt, history_trimmer
from src.schema import Query, Response
from src.tools import get_documents_from_json_folder, get_tools_from_type_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

embedding_function = OpenAIEmbeddings()
chroma_client = get_chroma_client()

law_documents = get_documents_from_json_folder("documents/laws")
case_documents = get_documents_from_json_folder("documents/cases")
upload_documents_to_chroma(chroma_client, "laws", embedding_function, law_documents)
upload_documents_to_chroma(chroma_client, "cases", embedding_function, case_documents)
law_tools = get_tools_from_type_client("laws", chroma_client, embedding_function)
case_tools = get_tools_from_type_client("cases", chroma_client, embedding_function)

functions = law_tools + case_tools + [Response]
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
llm_with_functions = llm.bind_functions(functions)

# Response must not be passed to tools for some reason, most probably since it is not a callable
agent = create_agent(prompt, llm_with_functions, parse_output_schema)
agent_executor = AgentExecutor(agent=agent, tools=law_tools + case_tools)

app = FastAPI(
    title="LangChain Server",
    version="0.1",
    description="A simple API server using the ainvoke runnable endpoint with support for chat_history over redis",
)


@app.get("/health")
def get_health():
    """Returns the health status of the service"""
    return {"status": "running"}


# TODO (OPT): Move to json object for input and session_id, consider encrypting session_id
@app.post("/invoke")
async def ainvoke(input: str, session_id: str) -> dict:
    """Returns the response from the chatbot for a given user query and chat session unique id"""
    # Check for missing input or session_id
    if not input or not session_id:
        logger.error("Input or session_id missing")
        raise HTTPException(status_code=400, detail="Input or session_id missing")
    try:
        # ttl is the time (in seconds) for that specific chat history to expire and get deleted
        message_history_handler = RedisChatMessageHistory(
            url="redis://{}:{}/0".format(
                os.environ["REDIS_HOST"], os.environ["REDIS_PORT"]
            ),
            ttl=600,
            session_id=session_id,
        )
        chat_history = message_history_handler.messages
        output = await agent_executor.ainvoke(
            {"input": input, "chat_history": history_trimmer(chat_history)}
        )
        message_history_handler.add_message(HumanMessage(content=input))
        message_history_handler.add_message(
            AIMessage(
                content=output["answer"],
                additional_kwargs={"sources": output["sources"]}, # TODO: Investigate if it is better to pass the source contents or just the uuids in the history
            )
        )
        logger.info(f"Response generated for session_id: {session_id}")
        return {"answer": output["answer"], "sources": parse_sources(output["sources"])}
    except HTTPException:
        logger.exception("Internal Server Error")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
