import json
import os

from langchain_core.agents import AgentActionMessageLog, AgentFinish


def parse_output_schema(output, output_schema_name="Response"):
    # If no function was invoked, return to user
    if "function_call" not in output.additional_kwargs:
        return AgentFinish(
            return_values={"answer": output.content, "sources": []}, log=output.content
        )

    # Parse out the function call
    function_call = output.additional_kwargs["function_call"]
    name = function_call["name"]
    inputs = json.loads(function_call["arguments"])

    # If the output_schema function was invoked, return to the user with the function inputs
    if name == output_schema_name:
        return AgentFinish(return_values=inputs, log=str(function_call))
    # Otherwise, return an agent action
    else:
        return AgentActionMessageLog(
            tool=name, tool_input=inputs, log="", message_log=[output]
        )

def parse_sources(source_uuids):
    source_contents = []
    for uuid in source_uuids:
        found = False
        if not found:
            for folder, _, files in os.walk("documents"):
                for file in files:
                    if file.lower().endswith(".json") and uuid in file:
                        found = True
                        file_path = os.path.join(folder, file)
                        with open(file_path, "r") as f:
                            json_data = json.load(f)
                            source_contents.append(json_data.get("content"))
    return source_contents
