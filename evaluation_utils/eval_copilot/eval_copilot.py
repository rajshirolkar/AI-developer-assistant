import re
import openai
import os

from dotenv import load_dotenv
from openai import OpenAI

from evaluation_utils.eval_copilot.copilot_eval_criteria import COHERENCE_PROMPT_TEMPLATE
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()
client.api_key = os.environ.get("OPENAI_API_KEY")


class EvaluationCopilot:
    def __init__(self, system_prompt, user_instructions, example_evaluations):
        self.example_evaluations = example_evaluations
        self.system_prompt = system_prompt
        self.user_instructions = user_instructions

    def _create_message(self, role, content):
        return {"role": role, "content": content}

    def __create_evaluation_messages(self, user_prompt):
        messages = []
        messages.append(self._create_message("system", self.system_prompt))
        messages.append(self._create_message("user", self.user_instructions))
        for user, assistant in self.example_evaluations:
            messages.append(self._create_message("user", user))
            messages.append(self._create_message("assistant", assistant))
        messages.append(self._create_message("user", user_prompt))
        return messages

    def _run_chat_completions(self, messages):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content

    def __parse_score_and_justification(self, full_response):
        score_match = re.search(r"Stars:\s*(\d+)", full_response)
        justification_match = re.search(r"Justification:\s*(.+)", full_response, re.DOTALL)

        score = score_match.group(1) if score_match else "0"
        justification = justification_match.group(1).strip() if justification_match else "No justification provided."
        return score, justification

    def get_score_and_justification(self, user_prompt, llm_response):
        prompt_and_response = f"Question:{user_prompt}\nAnswer:{llm_response}"
        messages = self.__create_evaluation_messages(prompt_and_response)
        full_response = self._run_chat_completions(messages)
        return self.__parse_score_and_justification(full_response)


def get_eval_score(client, user_prompt, response, prompt_template):
    # Construct the prompt with placeholders filled
    prompt = prompt_template.format(question=user_prompt, answer=response)

    # Call OpenAI API to evaluate
    try:
        api_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        full_response = api_response.choices[0].message.content
        print(full_response)

        score_match = re.search(r"Stars:\s*(\d+)", full_response)
        justification_match = re.search(r"Justification:\s*(.+?)(?=Improvement Suggestion:)", full_response, re.DOTALL)
        improvement_match = re.search(r"Improvement Suggestion:\s*(.+)", full_response, re.DOTALL)

        print(score_match, justification_match, improvement_match)
        # Extract the score, justification, and improvement suggestion
        score = score_match.group(1) if score_match else "0"
        justification = justification_match.group(1).strip() if justification_match else "No justification provided."
        improvement = improvement_match.group(1).strip() if improvement_match else "No improvement suggestion provided."

        return {
            "score": int(score),
            "justification": justification,
            "improvement_suggestion": improvement
        }
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return {
            "score": 0,
            "justification": "An error occurred during the evaluation.",
            "improvement_suggestion": ""
        }


def copilot_evaluation(user_prompt, response_text, client):
    evaluations = {}

    eval_result = get_eval_score(client, user_prompt, response_text, COHERENCE_PROMPT_TEMPLATE)
    evaluations['Coherence'] = eval_result

    return evaluations
