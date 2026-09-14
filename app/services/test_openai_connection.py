import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6-terra",
    )

    if not api_key:
        print("OPENAI_API_KEY is not configured.")
        return

    print("OpenAI API key found.")
    print(f"Testing model: {model}")

    client = OpenAI(
        api_key=api_key
    )

    response = client.responses.create(
        model=model,
        input=(
            "Reply with exactly this sentence: "
            "OpenAI connection successful."
        ),
    )

    print("\nOpenAI Response:")
    print(response.output_text)


if __name__ == "__main__":
    main()