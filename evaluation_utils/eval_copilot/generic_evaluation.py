from fastapi import HTTPException
from openai import OpenAI
import os
from dotenv import load_dotenv

from evaluation_utils.openai.openai_eval import get_simple_response

load_dotenv()
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")


def generic_evaluation(question, answer, client):
    system_prompt = """
        [System]
        Please act as an impartial judge and evaluate the quality of the response provided by an
        AI assistant to the user question displayed below. Your evaluation should consider factors
        such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of
        the response. Begin your evaluation by providing a short explanation. Be as objective as
        possible. After providing your explanation, please rate the response on a scale of 1 to 5
        by strictly following this format: "[[explanation]], [[the response could be improved by]],  [[rating]]", for example: "Explanation:[[explanation..]], Improvement Suggestions:[[the response could be improved by…]], Rating: [[5]]".
        [Question]
        {question}
        [The Start of Assistant’s Answer]
        {answer}
        [The End of Assistant’s Answer]
    """
    prompt = system_prompt.format(question=question, answer=answer)
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview", messages=[{"role": "system", "content": prompt}]
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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


# Example usage

# question = "How many countries were involved in the Napoleanic Wars?"
# answer = get_simple_response(question, client)
# print("Answer:", answer)
# response_text = generic_evaluation(question, answer, client)
# print("Response Text:", response_text)
# justification, improvement_suggestions, rating = parse_response(response_text)
# print("Justification:", justification)
# print("Improvement Suggestions:", improvement_suggestions)
# print("Rating:", rating)


def get_generic_evaluation_score(question, answer, client):
    response_text = generic_evaluation(question, answer, client)
    explanation, improvement_suggestions, rating = parse_response(response_text)
    return {
        "explanation": explanation,
        "improvement_suggestions": improvement_suggestions,
        "rating": rating,
    }
