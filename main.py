import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
from functions.call_function import call_function



load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
) 

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Lists file contents, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="lists the content of a given file",
            ),
        },
    ),
) 

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Runs a python file",
            ),
        },
    ),
) 

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="writes to a file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="file path to the written file",
    ),
    "content": types.Schema(
        type=types.Type.STRING,
        description="content written to file", 
            ),
        },
    ),
) 


available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file
    ]
)

config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)


def main():
    verbose = "--verbose" in sys.argv

    if len(sys.argv) < 2:
        print("Error, please provide a prompt")
        sys.exit(1)
    else:
        prompt = sys.argv[1]
        
        messages = [
    types.Content(role="user", parts=[types.Part(text=prompt)]),
]
        
        response = client.models.generate_content(model= "gemini-2.0-flash-001" , contents= messages, config= config)

    if response.function_calls:
        function_call_part = response.function_calls[0]
        function_call_result = call_function(function_call_part, verbose)

        if not function_call_result.parts[0].function_response.response:
            raise Exception("Function call result missing expected response structure")

        if verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")

    else:
        print(response.text)

    if verbose:
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


    




if __name__ == "__main__":
    main()


