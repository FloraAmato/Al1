import os
import json

from langchain_core.documents import Document


def load_documents_from_json(documents_folder):
    documents = []
    # TODO (OPT): Do not hardcode stuff, move them into a utility class, same goes for env vars
    keys = [
        "uuid",
        "CASE_ID",
        "cost",
        "duration",
        "law",
        "state",
        "type",
        "civil_codes_used",
        "law_type",
        "succession_type",
        "subject_of_succession",
        "testamentary_clauses",
        "disputed_issues",
        "relationship_between_parties",
        "number_of_persons_involved",
    ]
    # Loop through each file in the folder
    for filename in os.listdir(documents_folder):
        # Check if the file is a JSON file
        if filename.endswith(".json"):
            file_path = os.path.join(
                documents_folder, filename
            )  # Construct full file path
            # Open the JSON file and load its content
            with open(file_path, "r") as file:
                doc_json = json.load(file)
                doc_json["metadata"]["uuid"] = os.path.splitext(filename)[0]

                # Create a new Document object for each dictionary, unpacking the keys as arguments
                document = Document(
                    page_content=doc_json["content"],
                    metadata={
                        key: str(doc_json["metadata"][key])
                        for key in keys
                        if key in doc_json["metadata"].keys()
                    },
                )
                documents.append(document)
    return documents
