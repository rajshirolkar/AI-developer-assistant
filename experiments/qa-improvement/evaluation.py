import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.Client()

def chat_complete(prompt):
    response = client.chat.completions.create(
            model="gpt-4-1106-preview", messages=[{"role": "system", "content": prompt}]
        )
    generated_text = response.choices[0].message.content
    return generated_text

def parse_response(response_text):
    # Split the response into parts
    explanation = response_text.split("Explanation:")[1].split(
        "Improvement Suggestions:"
    )[0]
    print("Explanation : ", explanation)
    improvement_suggestions = response_text.split("Improvement Suggestions:")[1].split(
        "Rating:"
    )[0]
    print("Improvement Suggestions : ", improvement_suggestions)
    rating = response_text.split("Rating:")[1].replace("[[", "").replace("]]", "")
    print("Rating : ", rating)

    return explanation, improvement_suggestions, rating


def parse_improvement_response(response_text):
    question_improvement = response_text.split("Question Improvement:")[1].split(
        "Answer Improvement:"
    )[0].replace("[[", "").replace("]]", "")

    print("Question Improvement : ", question_improvement)
    answer_improvement = response_text.split("Answer Improvement:")[1].replace("[[", "").replace("]]", "")
    print("Answer Improvement : ", answer_improvement)

    return question_improvement, answer_improvement



evaluation_system_prompt_template = """
    [System]
    Please act as an impartial judge and evaluate the quality of the response provided by an
    AI assistant to the user question displayed below. Your evaluation should consider factors
    such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of
    the response. Begin your evaluation by providing a short explanation. Be as objective and concise as
    possible using simple language. The explanation should be 2-3 bullet points that are easy to glance over. After providing your explanation, please rate the response on a scale of 1 to 5
    by strictly following this format: "[[explanation]], [[the response could be improved by]],  [[rating]]", 
    for example: "Explanation:[[explanation..]], Improvement Suggestions:[[the response could be improved by…]], Rating: [[5]]".
    [Question]
    {question}
    [The Start of Assistant’s Answer]
    {answer}
    [The End of Assistant’s Answer]
"""

improvement_system_prompt_template = """
[System]
You are an expert in assessing AI Question Answer evaluation report. You will be given a short evaluation report of an AI response to a user question, with an
evaluation report giving you a score the QA pair received and an explanation of why a certain score was given. 
Based on the evaluation report, you will be required to provide suggestions on some improvements that can be made to the user's question and the AI's response.
Be as objective as possible and your suggestions should be actionable items in 2-3 bullets that can be quickly glanced over. 
Give your suggestions by strictly following this format: [[ question improvement suggestion ]], [[ answer improvement suggestion]].,
for example "Question Improvement: [[question improvement suggestion..]], Answer Improvement: [[answer improvement suggestion..]]".

[The Start of Evaluation Report]

[User's Question]
{question}

[The Start of Assistant’s Answer]
{answer}
[The End of Assistant’s Answer]

[Score]
{score}

[The Start of Explanation]
{explanation}
[The End of Explanation]

[The End of Evaluation Report]
"""

# evaluation_system_prompt_template = """
#     [System]
#     Please act as an impartial judge and evaluate the quality of the response provided by an
#     AI assistant to the user question displayed below. Your evaluation should consider factors
#     such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of
#     the response. Begin your evaluation by providing a short explanation. Be as objective as
#     possible. After providing your explanation, please rate the response on a scale of 1 to 5
#     by strictly following this format: "[[explanation]], [[the response could be improved by]],  [[rating]]", 
#     for example: "Explanation:[[explanation..]], Improvement Suggestions:[[the response could be improved by…]], Rating: [[5]]".
#     [Question]
#     {question}
#     [The Start of Assistant’s Answer]
#     {answer}
#     [The End of Assistant’s Answer]
# """

# improvement_system_prompt_template = """
# [System]
# You are an expert in assessing AI Question Answer evaluation report. You will be given a short evaluation report of an AI response to a user question, with an
# evaluation report giving you a score the QA pair received and an explanation of why a certain score was given. 
# Based on the evaluation report, you will be required to provide suggestions on some improvements that can be made to the user's question and the AI's response.
# Be as objective as possible. Give your suggestions by strictly following this format: [[ question improvement suggestion ]], [[ answer improvement suggestion]].,
# for example "Question Improvement: [[question improvement suggestion..]], Answer Improvement: [[answer improvement suggestion..]]".

# [The Start of Evaluation Report]

# [User's Question]
# {question}

# [The Start of Assistant's Answer]
# {answer}
# [The End of Assistant's Answer]

# [Score]
# {score}

# [The Start of Explanation]
# {explanation}
# [The End of Explanation]

# [The End of Evaluation Report]
# """

