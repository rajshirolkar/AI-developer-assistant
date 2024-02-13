from evaluation_utils.eval_copilot.copilot_utils import (
    create_message,
    run_chat_completions,
    parse_score_and_justification_words,
    parse_improvement_suggestion,
)
from evaluation_utils.openai.openai_eval import get_simple_response

simplicity_system_prompt = """You are an AI assistant. You will be given the definition of an evaluation metric for 
assessing the quality of an answer in a question-answering task. Your job is to compute an accurate evaluation score 
using the provided evaluation metric."""

# relevance_user_instructions = """
# Relevance measures how well the answer addresses the main aspects of the question, based on the context. Consider whether all and only the important aspects are contained in the answer when evaluating relevance. Given the context and question, score the relevance of the answer between one to five stars using the following rating scale:
# One star: the answer completely lacks relevance
# Two stars: the answer mostly lacks relevance
# Three stars: the answer is partially relevant
# Four stars: the answer is mostly relevant
# Five stars: the answer has perfect relevance
#
# This rating value should always be an integer between 1 and 5. So the rating produced should be 1 or 2 or 3 or 4 or 5.
# """

simplicity_user_instructions = """
Simplicity measures the conciseness and ease of understanding of the answer, while it still addresses the main aspects of the question. Evaluate simplicity by considering the answer's length, lexical complexity, and its overall comprehensibility. Given the context and question, score the simplicity of the answer using the following Likert scale:
- "Very Bad": the answer completely lacks simple and is hard to understand
- "Bad": the answer mostly lacks simple and is difficult to understand
- "Average": the answer is partially simple and is somewhat easy to understand
- "Good": the answer is mostly simple and is easy to understand
- "Very Good": the answer is perfectly simple and is very easy to understand

This rating should reflect the degree of simplicity. Choose from "Very Bad", "Bad", "Average", "Good", or "Very Good" to represent the simplicity score.

"""

simplicity_improvement_system_prompt = """
You are an AI assistant designed to suggest improvements for question-answering tasks. Based on the provided context, question, answer, simplicity score, and justification, your task is to analyze the information and suggest specific improvements that can enhance the simplicity and accuracy of the answer. Focus on providing clear, actionable feedback that addresses any identified shortcomings in the provided answer.
"""

simplicity_improvement_instructions = """
When suggesting improvements, consider the following:
1. Analyze the simplicity score and justification. Use these to identify specific areas where the answer can be improved.
2. If the score is low, focus on fundamental changes to the answer that can address major inaccuracies or complexity issues.
3. For higher scores, suggest minor adjustments or additional details that could further simplify the answer, ensuring it remains relevant and informative within the given context.
4. Ensure your suggestions are specific and directly related to the content of the question and answer. Vague or general advice should be avoided.
5. Consider the context provided. The suggested improvements should aim to make the answer more straightforward and understandable, while still conveying information effectively.
"""

simplicity_few_shot_examples = [
    {
        "context": "The theory of relativity was developed by Albert Einstein, fundamentally altering our understanding of physics.",
        "question": "Who formulated the theory of relativity?",
        "answer": "The theory, which involves complex mathematical constructs for predicting celestial movements, was theorized by a scientist famous for his equation, E=mc².",
        "stars": "Very Bad",
        "justification": "The answer is overly complex, failing to directly name Albert Einstein and using convoluted language that makes it hard to understand. It doesn't straightforwardly address the question.",
        "improvement_suggestion": "Simplify the answer by directly stating, 'Albert Einstein formulated the theory of relativity.' This is concise and directly addresses the question.",
    },
    {
        "context": "Photosynthesis is a process used by plants to convert light energy into chemical energy.",
        "question": "What is photosynthesis?",
        "answer": "A biological procedure where plants transform luminosity into a form that can be stored and used for growth.",
        "stars": "Bad",
        "justification": "The answer, while somewhat addressing the question, uses unnecessarily complex terms like 'luminosity' instead of 'light' and 'biological procedure,' making it harder to understand.",
        "improvement_suggestion": "Make the explanation simpler by saying, 'Photosynthesis is how plants use sunlight to make food.'",
    },
    {
        "context": "Bitcoin is a digital currency that operates without a central authority or banks.",
        "question": "What is Bitcoin?",
        "answer": "Bitcoin is an online form of money that is managed by a network of computers and is not reliant on any governmental or banking institutions.",
        "stars": "Average",
        "justification": "The answer is moderately simple and understandable, but it could be more concise and use more common terminology.",
        "improvement_suggestion": "A simpler answer would be, 'Bitcoin is a digital currency that works independently of banks and governments.'",
    },
    {
        "context": "The Great Wall of China was built to protect against invasions and raids from different nomadic groups.",
        "question": "Why was the Great Wall of China built?",
        "answer": "To defend against attacks from nomads.",
        "stars": "Good",
        "justification": "The answer is mostly simple and easy to understand, summarizing the main point succinctly.",
        "improvement_suggestion": "For slight improvement, mention that it was built for protection, making it 'The Great Wall of China was built to protect against nomadic invasions.'",
    },
    {
        "context": "Water boils at 100 degrees Celsius under standard atmospheric conditions.",
        "question": "At what temperature does water boil?",
        "answer": "Water boils at 100 degrees Celsius.",
        "stars": "Very Good",
        "justification": "The answer is perfectly simple and very easy to understand, directly addressing the question with precise information.",
        "improvement_suggestion": "No improvement needed, as the answer is already concise and directly relevant to the question.",
    },
]


simplicity_evaluation_prompt = {
    "system": simplicity_system_prompt,
    "user": simplicity_user_instructions,
    "examples": simplicity_few_shot_examples,
}

simplicity_improvement_prompts = {
    "system": simplicity_improvement_system_prompt,
    "user": simplicity_improvement_instructions,
    "evaluation_system": simplicity_system_prompt,
    "evaluation_instructions": simplicity_user_instructions,
    "examples": simplicity_few_shot_examples,
}


class EvaluationCopilotNew:
    def __init__(self, evaluation_prompt):
        self.system_prompt = evaluation_prompt["system"]
        self.user_instructions = evaluation_prompt["user"]
        self.example_evaluations = self.__format_examples(evaluation_prompt["examples"])

    def __format_examples(self, examples):
        formatted_examples = []
        for example in examples:
            user = f"Context: {example['context']}\nQuestion: {example['question']}\nAnswer: {example['answer']}"
            assistant = f"Stars:{example['stars']}"
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


class ImprovementCopilotNew(EvaluationCopilotNew):
    def __init__(self, improvement_prompt):
        super().__init__(
            {
                "system": improvement_prompt["evaluation_system"],
                "user": improvement_prompt["evaluation_instructions"],
                "examples": improvement_prompt["examples"]
                if improvement_prompt["examples"]
                else None,
            }
        )
        self.example_improvement_suggestions = (
            [
                example["improvement_suggestion"]
                for example in improvement_prompt["examples"]
            ]
            if improvement_prompt["examples"]
            else None
        )
        self.improvement_system_prompt = improvement_prompt["system"]
        self.improvement_instructions = improvement_prompt["user"]

    def __create_improvement_messages(self, user_prompt):
        messages = [create_message("system", self.improvement_system_prompt)]
        if self.improvement_instructions:
            messages.append(create_message("user", self.improvement_instructions))
        if self.example_improvement_suggestions:
            for i, (user, assistant) in enumerate(self.example_evaluations):
                messages.append(create_message("user", user + "\n" + assistant))
                messages.append(
                    create_message("assistant", self.example_improvement_suggestions[i])
                )
        messages.append(create_message("user", user_prompt))
        return messages

    def get_improvement_suggestion(self, context, user_prompt, llm_response):
        score, justification = self.get_score_and_justification(
            context, user_prompt, llm_response
        )
        print("Score:", score)
        print("Justification:", justification)
        extended_user_prompt = f"Question: {user_prompt}\nAnswer: {llm_response}\nStars: {score}\nJustification: {justification}"
        print("Extended User Prompt:", extended_user_prompt)
        messages = self.__create_improvement_messages(extended_user_prompt)
        full_response = run_chat_completions(messages)
        print("Full Response:", full_response)
        improvement_suggestion = parse_improvement_suggestion(full_response)
        print("Improvement Suggestion:", improvement_suggestion)
        return score, justification, improvement_suggestion


# improvement_copilot = ImprovementCopilotNew(relevance_improvement_prompts)


# import openai
# from openai import OpenAI
# import os
# import re
# import pandas as pd
# from dotenv import load_dotenv
#
# load_dotenv()
#
# openai.api_key = "OPENAI_API_KEY"
# client = OpenAI()
# client.api_key = os.getenv("OPENAI_API_KEY")
# print("API Key:", client.api_key)
# prompt = "How many countries were involved in the Napoleanic Wars?"
# ground_truth = """
# Napoleonic Wars, (1799–1815) Series of wars that ranged France against shifting alliances of European powers. Originally an attempt to maintain French strength established by the French Revolutionary Wars, they became efforts by Napoleon to affirm his supremacy in the balance of European power. A victory over Austria at the Battle of Marengo (1800) left France the dominant power on the continent. Only Britain remained strong, and its victory at the Battle of Trafalgar (1805) ended Napoleon’s threat to invade England. Napoleon won major victories in the Battles of Ulm and Austerlitz (1805), Jena and Auerstedt (1806), and Friedland (1807) against an alliance of Russia, Austria, and Prussia. The resulting Treaties of Tilsit (1807) and the Treaty of Schönbrunn (1809) left most of Europe from the English Channel to the Russian border either part of the French Empire, controlled by France, or allied to it by treaty. Napoleon’s successes resulted from a strategy of moving his army rapidly, attacking quickly, and defeating each of the disconnected enemy units. His enemies’ responding strategy was to avoid engagement while withdrawing, forcing Napoleon’s supply lines to be overextended; the strategy was successfully used against him by the duke of Wellington in the Peninsular War and by Mikhail, Prince Barclay de Tolly, in Russia. In 1813 the Quadruple Alliance formed to oppose Napoleon and amassed armies that outnumbered his. Defeated at the Battle of Leipzig, he was forced to withdraw west of the Rhine River, and after the invasion of France (1814) he abdicated. He rallied a new army to return in the Hundred Days (1815), but a revived Quadruple Alliance opposed him. His final defeat at the Battle of Waterloo was caused by his inability to surprise and to prevent the two armies, led by Wellington and Gebhard von Blücher, from joining forces to defeat him. With his second abdication and exile, the era of the Napoleonic Wars ended.
# """
# response = get_simple_response(prompt, client)
# print(response)
# print(
#     "Improvement Copilot:",
#     improvement_copilot.get_improvement_suggestion(ground_truth, prompt, response),
# )
