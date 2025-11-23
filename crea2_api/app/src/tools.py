import os

from langchain_core.prompts import PromptTemplate
from langchain.tools.retriever import create_retriever_tool
from .chroma import get_chroma_vectorstore
from .document_loader import load_documents_from_json


def _create_retriever_tool_per_topic_country(
    vectorstore, type, topic, country, name, description
):
    # In this tool, filters are applied to vectorstores prior the search!
    # Alternatively, you can filter later with vectorstore.similarity_search("foo", filter=dict(page=1), k=1, fetch_k=4)
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "filter": {
                "$and": [
                    {"law": {"$eq": topic}},
                    {"$or": [{"type": {"$eq": country}}, {"state": {"$eq": country}}]},
                ]
            }  # Using Chroma syntax for where statement, $or is just because metadata between laws and cases mismatch, optional k specifies how many documents to retrieve
        },
    )
    # document_prompt specifies how the retrieved documents should look like to the language model
    if type == "laws":
        template = "uuid: {uuid}\narticle_number: {civil_codes_used}\narticle_text: {page_content}"
    else:  # type == "cases"
        template = "uuid: {uuid}\ncivil_codes_used: {civil_codes_used}\ncost: {cost}\nduration: {duration}\ntype: {type}\nlaw_type: {law_type}\nsuccession_type: {succession_type}\nsubject_of_succession: {subject_of_succession}\ntestamentary_clauses: {testamentary_clauses}\ndisputed_issues: {disputed_issues}\nrelationship_between_parties: {relationship_between_parties}\nnumber_of_persons_involved: {number_of_persons_involved}\nsummary: {page_content}"
    retriever_tool = create_retriever_tool(
        retriever,
        name,
        description,
        document_prompt=PromptTemplate.from_template(template),
        document_separator="\n--- NEXT DOCUMENT ---\n",
    )
    return retriever_tool


def get_documents_from_json_folder(json_folder):
    documents = []
    for relative_documents_folder in os.listdir(json_folder):
        documents_folder = os.path.join(json_folder, relative_documents_folder)
        documents += load_documents_from_json(documents_folder)
    return documents


# TODO (OPT): Law tools should support lookup by article number while case tools should support filtering after search!
def get_tools_from_type_client(type, chroma_client, embedding_function):
    assert type in ["laws", "cases"]
    topics = ["Divorce", "Inheritance"]
    countries = ["BELGIUM", "CROATIA", "ESTONIA", "ITALY", "LITHUANIA", "SLOVENIA"]

    tools = []
    vectorstore = get_chroma_vectorstore(chroma_client, type, embedding_function)
    for topic in topics:
        for country in countries:
            tools.append(
                _create_retriever_tool_per_topic_country(
                    vectorstore,
                    type,
                    topic,
                    country,
                    f"{topic}_{country}_{type}",
                    f"Query a retriever to get information about {topic.lower()}-related {type} in {country.capitalize()}.",
                )
            )
    return tools
