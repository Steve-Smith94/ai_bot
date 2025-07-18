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

# Your schema definitions (same as before)
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

config = types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)

def main():
    verbose = "--verbose" in sys.argv

    if len(sys.argv) < 2:
        print("Error, please provide a prompt")
        sys.exit(1)
    else:
        prompt = sys.argv[1]
        
    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]   
    
    for iteration in range(20):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001", 
                contents=messages, 
                config=config
            )

            # Add model response to conversation
            for candidate in response.candidates:
                messages.append(candidate.content)

            # Check for function calls and execute them
            function_responses = []
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        if verbose:
                            print(f" - Calling function: {part.function_call.name}")
                        
                        # Get the result from call_function (it returns a Content object)
                        result_content = call_function(part.function_call, verbose)
                        
                        # Extract the function response data from the first part
                        if result_content.parts and hasattr(result_content.parts[0], 'function_response'):
                            function_response_data = result_content.parts[0].function_response.response
                        else:
                            # Fallback - create response data from the content
                            function_response_data = {"result": str(result_content)}
                        
                        # Create a proper function response part
                        function_response = types.Part(
                            function_response=types.FunctionResponse(
                                name=part.function_call.name,
                                response=function_response_data
                            )
                        )
                        function_responses.append(function_response)

            # If we had function calls, add their results as tool messages
            if function_responses:
                messages.append(types.Content(role="tool", parts=function_responses))
            elif response.text:
                # No function calls and we have final text
                print("Final response:")
                print(response.text)
                break

        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()

