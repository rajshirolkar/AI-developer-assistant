from evaluation_utils.eval_copilot.copilot_utils import (
    create_message,
    run_chat_completions,
    parse_score_and_justification_words,
    parse_improvement_suggestion,
)
from evaluation_utils.openai.openai_eval import get_simple_response

relevance_system_prompt = """You are an AI assistant. You will be given the definition of an evaluation metric for 
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

relevance_user_instructions = """
Relevance measures how well the answer addresses the main aspects of the question, based on the context. Consider whether all and only the important aspects are contained in the answer when evaluating relevance. Given the context and question, score the relevance of the answer using the following Likert scale:
- "Very Bad": the answer completely lacks relevance
- "Bad": the answer mostly lacks relevance
- "Average": the answer is partially relevant
- "Good": the answer is mostly relevant
- "Very Good": the answer has perfect relevance

This rating should reflect the degree of relevance. Choose from "Very Bad", "Bad", "Average", "Good", or "Very Good" to represent the relevance score.

"""

relevance_improvement_system_prompt = """
You are an AI assistant designed to suggest improvements for question-answering tasks. Based on the provided context, question, answer, relevance score, and justification, your task is to analyze the information and suggest specific improvements that can enhance the relevance and accuracy of the answer. Focus on providing clear, actionable feedback that addresses any identified shortcomings in the provided answer.
"""

relevance_improvement_instructions = """
When suggesting improvements, consider the following:
1. Analyze the relevance score and justification. Use these to identify specific areas where the answer can be improved.
2. If the score is low, focus on fundamental changes to the answer that can address major inaccuracies or relevance issues.
3. For higher scores, suggest minor adjustments or additional details that could further improve the answer's alignment with the question and context.
4. Ensure your suggestions are specific and directly related to the content of the question and answer. Vague or general advice should be avoided.
5. Consider the context provided. The improvement should make the answer more relevant and informative in light of the given context.
"""

relevance_few_shot_examples = [
    {
        "context": "Marie Curie was a Polish-born physicist and chemist who pioneered research on radioactivity and was the first woman to win a Nobel Prize.",
        "question": "What field did Marie Curie excel in?",
        "answer": "Marie Curie was a renowned painter who focused mainly on impressionist styles and techniques.",
        "stars": "Very Bad",
        "justification": "The answer is completely irrelevant as it incorrectly identifies Marie Curie as a painter, whereas she was actually a physicist and chemist. The answer fails to address the main aspect of the question, which is her field of expertise.",
        "improvement_suggestion": "Correct the answer to reflect Marie Curie's true field of expertise. An improved answer would state that Marie Curie was a notable physicist and chemist known for her research on radioactivity.",
    },
    {
        "context": "The Beatles were an English rock band formed in Liverpool in 1960, and they are widely regarded as the most influential music band in history.",
        "question": "Where were The Beatles formed?",
        "answer": "The band The Beatles began their journey in London, England, and they changed the history of music.",
        "stars": "Bad",
        "justification": "The answer mostly lacks relevance as it provides incorrect information about the formation location of The Beatles. The question explicitly asks for the place of formation, and the answer incorrectly states London instead of Liverpool.",
        "improvement_suggestion": "Correct the geographical error in the answer. An improved answer would correctly state that The Beatles were formed in Liverpool, England.",
    },
    {
        "context": "The recent Mars rover, Perseverance, was launched in 2020 with the main goal of searching for signs of ancient life on Mars. The rover also carries an experiment called MOXIE, which aims to generate oxygen from the Martian atmosphere.",
        "question": "What are the main goals of Perseverance Mars rover mission?",
        "answer": "The Perseverance Mars rover mission focuses on searching for signs of ancient life on Mars.",
        "stars": "Average",
        "justification": "The answer is partially relevant. It correctly identifies one of the main goals of the Perseverance rover – searching for ancient life. However, it omits other key aspects like the MOXIE experiment, which is also a significant part of the mission's goals.",
        "improvement_suggestion": "Expand the answer to include more goals of the mission. An improved answer would mention the MOXIE experiment for generating oxygen from the Martian atmosphere, along with the search for ancient life.",
    },
    {
        "context": "The Mediterranean diet is a commonly recommended dietary plan that emphasizes fruits, vegetables, whole grains, legumes, lean proteins, and healthy fats. Studies have shown that it offers numerous health benefits, including a reduced risk of heart disease and improved cognitive health.",
        "question": "What are the main components of the Mediterranean diet?",
        "answer": "The Mediterranean diet primarily consists of fruits, vegetables, whole grains, and legumes.",
        "stars": "Good",
        "justification": "The answer is mostly relevant. It accurately lists several main components of the Mediterranean diet, such as fruits, vegetables, whole grains, and legumes. However, it misses out on mentioning lean proteins and healthy fats, which are also important aspects of this diet.",
        "improvement_suggestion": "Include all key components of the Mediterranean diet in the answer. An improved answer would also mention lean proteins and healthy fats, in addition to the already listed components.",
    },
    {
        "context": "The Queen's Royal Castle is a well-known tourist attraction in the United Kingdom. It spans over 500 acres and contains extensive gardens and parks. The castle was built in the 15th century and has been home to generations of royalty.",
        "question": "What are the main attractions of the Queen's Royal Castle?",
        "answer": "The main attractions of the Queen's Royal Castle are its expansive 500-acre grounds, extensive gardens, parks, and the historical castle itself, which dates back to the 15th century and has housed generations of royalty.",
        "stars": "Very Good",
        "justification": "The answer has perfect relevance. It comprehensively addresses all the important aspects of the question, covering the extensive grounds, gardens, parks, the historical significance of the castle, and its connection to generations of royalty, which aligns precisely with the context provided.",
        "improvement_suggestion": "No improvement needed. The answer perfectly addresses the question and aligns with the context provided.",
    },
]


relevance_evaluation_prompt = {
    "system": relevance_system_prompt,
    "user": relevance_user_instructions,
    "examples": relevance_few_shot_examples,
}

relevance_improvement_prompts = {
    "system": relevance_improvement_system_prompt,
    "user": relevance_improvement_instructions,
    "evaluation_system": relevance_system_prompt,
    "evaluation_instructions": relevance_user_instructions,
    "examples": relevance_few_shot_examples,
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
