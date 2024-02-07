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
    response = client.chat.completions.create(
        model="gpt-4-1106-preview", messages=messages
    )
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


def parse_score_and_justification_words(full_response):
    score_map = {
        "Very Bad": "1",
        "Bad": "2",
        "Average": "3",
        "Good": "4",
        "Very Good": "5",
    }

    score_match = re.search(
        r"Stars:\s*(Very Bad|Bad|Average|Good|Very Good)\s*", full_response, re.DOTALL
    )
    justification_match = re.search(r"Justification:\s*(.+)", full_response, re.DOTALL)

    score = score_map[score_match.group(1)] if score_match else "0"
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
        improvement_match.group(1).strip() if improvement_match else full_response
    )
    return improvement_suggestion
