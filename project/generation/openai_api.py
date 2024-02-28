import os
import json

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

api = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
)


def complete(messages: list[dict]) -> dict:
    return json.loads(
        api.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            temperature=1,
        ).choices[0].message.content,
        strict=False
    )
