import re
import openai
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()
client.api_key = os.environ.get("OPENAI_API_KEY")


def create_message(role, content):
    return {"role": role, "content": content}


def run_chat_completions(messages):
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content


def parse_score_and_justification(full_response):
    score_match = re.search(r"Stars:\s*(\d+)", full_response)
    justification_match = re.search(r"Justification:\s*(.+)", full_response, re.DOTALL)

    score = score_match.group(1) if score_match else "0"
    justification = (
        justification_match.group(1).strip()
        if justification_match
        else "No justification provided."
    )
    return score, justification


def parse_improvement_suggestion(full_response):
    improvement_match = re.search(
        r"Improvement Suggestion:\s*(.+)", full_response, re.DOTALL
    )
    improvement_suggestion = (
        improvement_match.group(1).strip()
        if improvement_match
        else "No improvement suggestion provided."
    )
    return improvement_suggestion
