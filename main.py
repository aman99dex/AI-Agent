import os
import sys
from functions.call_function import available_functions, call_function
from prompts import system_prompt
from dotenv import load_dotenv
from google import genai
from google.genai import Client, types


MODEL = "gemini-2.0-flash-001"
MAX_ITERATIONS = 20


def main():
    _ = load_dotenv()

    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I fix the calculator?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]

    i = 0
    while True:
        i += 1
        if i > MAX_ITERATIONS:
            print(f"Maximum iterations ({MAX_ITERATIONS}) reached.")
            sys.exit(1)
        try:
            final_response = generate_content(client, messages, verbose)
            if final_response:
                print("Final response:")
                print(final_response)
                break
        except Exception as e:
            print(f"Error in generate_content: {e}")



def generate_content(client: Client, messages: list[types.Content], verbose: bool) -> None|str:
    resp = client.models.generate_content( # pyright:ignore[reportUnknownMemberType]
        model=MODEL,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt
        ),
    )

    if verbose and resp.usage_metadata:
        print(f"Prompt tokens: {resp.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {resp.usage_metadata.candidates_token_count}")

    if resp.candidates:
        for candidate in resp.candidates:
            function_call_content = candidate.content
            if function_call_content:
                messages.append(function_call_content)

    if not resp.function_calls:
        return resp.text

    function_responses: list[types.Part] = []
    for function_call_part in resp.function_calls:
        result = call_function(function_call_part, verbose)
        if not result:
            raise Exception(f"no result from calling \"{function_call_part.name}\" with args \"{function_call_part.args}\"")

        if (
            not result.parts
            or not result.parts[0].function_response
        ):
            raise Exception("empty function call result")

        if verbose:
            print(f"-> {result.parts[0].function_response.response}")
        function_responses.append(result.parts[0])

    if not function_responses:
        raise Exception("no function responses generated, exiting.")

    messages.append(types.Content(role="tool", parts=function_responses))
    # print(resp.text)


if __name__ == "__main__":
    main()