import re

from evaluation_utils.eval_copilot.eval_copilot import EvaluationCopilot


# %%
class ImprovementCopilot(EvaluationCopilot):
    def __init__(self, improvement_system_prompt, improvement_instructions, evaluation_system_prompt, evaluation_instructions, few_shot_examples):
        # Extracting the first two elements for the base class
        evaluation_examples = [(user, assistant) for user, assistant, _ in few_shot_examples]
        super().__init__(evaluation_system_prompt, evaluation_instructions, evaluation_examples)
        self.example_improvement_suggestions = few_shot_examples
        self.improvement_system_prompt = improvement_system_prompt
        self.improvement_instructions = improvement_instructions

    def __create_improvement_messages(self, user_prompt):
        messages = []
        messages.append(self._create_message("system", self.improvement_system_prompt))
        messages.append(self._create_message("user", self.improvement_instructions))
        for user, assistant, improvement in self.example_improvement_suggestions:
            messages.append(self._create_message("user", user + "\n" + assistant))
            messages.append(self._create_message("assistant", improvement))
        messages.append(self._create_message("user", user_prompt))
        return messages

    def __parse_improvement_suggestion(self, full_response):
        improvement_match = re.search(r"Improvement Suggestion:\s*(.+)", full_response, re.DOTALL)
        improvement_suggestion = improvement_match.group \
            (1).strip() if improvement_match else "No improvement suggestion provided."
        return improvement_suggestion

    def get_improvement_suggestion(self, user_prompt, llm_response):
        score, justification = self.get_score_and_justification(user_prompt, llm_response)
        # print("Score:", score)
        # print("Justification:", justification)
        extended_user_prompt = f"Question: {user_prompt}\nAnswer: {llm_response}\nStars: {score}\nJustification: {justification}"
        print("Extended User Prompt:", extended_user_prompt)
        messages = self.__create_improvement_messages(extended_user_prompt)
        # print("Messages:", messages)
        full_response = self._run_chat_completions(messages)
        print("Full Response:", full_response)
        improvement_suggestion = self.__parse_improvement_suggestion(full_response)
        return score, justification, improvement_suggestion
