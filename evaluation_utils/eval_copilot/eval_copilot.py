import re


from evaluation_utils.eval_copilot.copilot_eval_criteria import (
    COHERENCE_PROMPT_TEMPLATE,
)
from evaluation_utils.eval_copilot.copilot_utils import (
    create_message,
    run_chat_completions,
    parse_score_and_justification,
    parse_score_and_justification_words,
)


# def create_message(role, content):
#     return {"role": role, "content": content}
#
#
# def run_chat_completions(messages):
#     response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
#     return response.choices[0].message.content
#
#
# def parse_score_and_justification(full_response):
#     score_match = re.search(r"Stars:\s*(\d+)", full_response)
#     justification_match = re.search(r"Justification:\s*(.+)", full_response, re.DOTALL)
#
#     score = score_match.group(1) if score_match else "0"
#     justification = (
#         justification_match.group(1).strip()
#         if justification_match
#         else "No justification provided."
#     )
#     return score, justification


class EvaluationCopilot:
    def __init__(self, system_prompt, user_instructions=None, example_evaluations=None):
        self.system_prompt = system_prompt
        self.example_evaluations = example_evaluations
        self.user_instructions = user_instructions

    def __create_evaluation_messages(self, user_prompt):
        messages = [create_message("system", self.system_prompt)]

        if self.user_instructions:
            messages.append(create_message("user", self.user_instructions))
        if self.example_evaluations:
            for user, assistant in self.example_evaluations:
                messages.append(create_message("user", user))
                messages.append(create_message("assistant", assistant))

        messages.append(create_message("user", user_prompt))
        return messages

    def get_score_and_justification(self, user_prompt, llm_response):
        prompt_and_response = f"Question:{user_prompt}\nAnswer:{llm_response}"
        messages = self.__create_evaluation_messages(prompt_and_response)
        full_response = run_chat_completions(messages)
        print("Full Response:", full_response)
        return parse_score_and_justification(full_response)


class EvaluationCopilotNew:
    def __init__(self, evaluation_prompt):
        self.system_prompt = evaluation_prompt["system"]
        self.user_instructions = evaluation_prompt["user"]
        self.example_evaluations = self.__format_examples(evaluation_prompt["examples"])

    def __format_examples(self, examples):
        formatted_examples = []
        for example in examples:
            user = f"Context: {example['context']}\nQuestion: {example['question']}\nAnswer: {example['answer']}"
            assistant = f"Stars: {example['stars']}"
            if "justification" in example:
                assistant += f"\nJustification: {example['justification']}"
            formatted_examples.append((user, assistant))
        return formatted_examples

    def __create_evaluation_messages(self, user_prompt):
        messages = [create_message("system", self.system_prompt)]

        if self.user_instructions:
            messages.append(create_message("user", self.user_instructions))
        for user, assistant in self.example_evaluations:
            messages.append(create_message("user", user))
            messages.append(create_message("assistant", assistant))

        messages.append(create_message("user", user_prompt))
        return messages

    def get_score_and_justification(self, context, user_prompt, llm_response):
        prompt_and_response = (
            f"Context: {context}\nQuestion:{user_prompt}\nAnswer:{llm_response}"
        )
        messages = self.__create_evaluation_messages(prompt_and_response)
        full_response = run_chat_completions(messages)
        print("Full Response:", full_response)
        return parse_score_and_justification_words(full_response)


def get_eval_score(client, user_prompt, response, prompt_template):
    # Construct the prompt with placeholders filled
    prompt = prompt_template.format(question=user_prompt, answer=response)

    # Call OpenAI API to evaluate
    try:
        api_response = client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": prompt}]
        )
        full_response = api_response.choices[0].message.content
        print(full_response)

        score_match = re.search(r"Stars:\s*(\d+)", full_response)
        justification_match = re.search(
            r"Justification:\s*(.+?)(?=Improvement Suggestion:)",
            full_response,
            re.DOTALL,
        )
        improvement_match = re.search(
            r"Improvement Suggestion:\s*(.+)", full_response, re.DOTALL
        )

        print(score_match, justification_match, improvement_match)
        # Extract the score, justification, and improvement suggestion
        score = score_match.group(1) if score_match else "0"
        justification = (
            justification_match.group(1).strip()
            if justification_match
            else "No justification provided."
        )
        improvement = (
            improvement_match.group(1).strip()
            if improvement_match
            else "No improvement suggestion provided."
        )

        return {
            "score": int(score),
            "justification": justification,
            "improvement_suggestion": improvement,
        }
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return {
            "score": 0,
            "justification": "An error occurred during the evaluation.",
            "improvement_suggestion": "",
        }


def copilot_evaluation(user_prompt, response_text, client):
    evaluations = {}

    eval_result = get_eval_score(
        client, user_prompt, response_text, COHERENCE_PROMPT_TEMPLATE
    )
    evaluations["Coherence"] = eval_result

    return evaluations
