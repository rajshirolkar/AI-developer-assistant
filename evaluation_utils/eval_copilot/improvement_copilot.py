import re

from evaluation_utils.eval_copilot.copilot_utils import (
    create_message,
    run_chat_completions,
    parse_improvement_suggestion,
)
from evaluation_utils.eval_copilot.eval_copilot import EvaluationCopilot


class ImprovementCopilot(EvaluationCopilot):
    def __init__(
        self,
        improvement_system_prompt,
        evaluation_system_prompt,
        improvement_instructions=None,
        evaluation_instructions=None,
        few_shot_examples=None,
    ):
        # Extracting the first two elements for the base class
        evaluation_examples = []
        if few_shot_examples:
            evaluation_examples = [
                (user, assistant) for user, assistant, _ in few_shot_examples
            ]
        super().__init__(
            evaluation_system_prompt,
            evaluation_instructions,
            evaluation_examples if evaluation_examples else None,
        )
        self.example_improvement_suggestions = few_shot_examples
        self.improvement_system_prompt = improvement_system_prompt
        self.improvement_instructions = improvement_instructions

    def __create_improvement_messages(self, user_prompt):
        messages = [create_message("system", self.improvement_system_prompt)]
        if self.improvement_instructions:
            messages.append(create_message("user", self.improvement_instructions))
        if self.example_improvement_suggestions:
            for user, assistant, improvement in self.example_improvement_suggestions:
                messages.append(create_message("user", user + "\n" + assistant))
                messages.append(create_message("assistant", improvement))
        messages.append(create_message("user", user_prompt))
        return messages

    def get_improvement_suggestion(self, user_prompt, llm_response):
        score, justification = self.get_score_and_justification(
            user_prompt, llm_response
        )
        # print("Score:", score)
        # print("Justification:", justification)
        extended_user_prompt = f"Question: {user_prompt}\nAnswer: {llm_response}\nStars: {score}\nJustification: {justification}"
        print("Extended User Prompt:", extended_user_prompt)
        messages = self.__create_improvement_messages(extended_user_prompt)
        # print("Messages:", messages)
        full_response = run_chat_completions(messages)
        print("Full Response:", full_response)
        improvement_suggestion = parse_improvement_suggestion(full_response)
        return score, justification, improvement_suggestion
