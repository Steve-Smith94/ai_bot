import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def main():
    if len(sys.argv) < 2:
        print("Error, please provide a prompt")
        sys.exit(1)
    else:
        prompt = sys.argv[1]
        
        messages = [
    types.Content(role="user", parts=[types.Part(text=prompt)]),
]
        
        api_call = client.models.generate_content(model= "gemini-2.0-flash-001" , contents= messages)

        print(api_call.text)

    if "--verbose" in sys.argv:
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {api_call.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {api_call.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
    main()


