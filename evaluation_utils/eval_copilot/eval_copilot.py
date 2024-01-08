import re

from evaluation_utils.eval_copilot.copilot_eval_criteria import COHERENCE_PROMPT_TEMPLATE


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
