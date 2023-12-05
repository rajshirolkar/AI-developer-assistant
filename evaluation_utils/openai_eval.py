from evaluation_utils.openai_eval_criteria import (
    CONSISTENCY_SCORE_CRITERIA,
    CONSISTENCY_SCORE_STEPS,
    EVALUATION_PROMPT_TEMPLATE,
    FLUENCY_SCORE_CRITERIA,
    FLUENCY_SCORE_STEPS,
    RELEVANCY_SCORE_CRITERIA,
    RELEVANCY_SCORE_STEPS,
    COHERENCE_SCORE_CRITERIA,
    COHERENCE_SCORE_STEPS,
)


def evaluate_response(response_text, client):
    evaluation_metrics = {
        "Relevance": (RELEVANCY_SCORE_CRITERIA, RELEVANCY_SCORE_STEPS),
        "Coherence": (COHERENCE_SCORE_CRITERIA, COHERENCE_SCORE_STEPS),
        "Consistency": (CONSISTENCY_SCORE_CRITERIA, CONSISTENCY_SCORE_STEPS),
        "Fluency": (FLUENCY_SCORE_CRITERIA, FLUENCY_SCORE_STEPS),
    }

    scores = {}
    for eval_type, (criteria, steps) in evaluation_metrics.items():
        score = get_geval_score(client, criteria, steps, response_text, eval_type)
        scores[eval_type] = score.strip()

    return scores

def get_geval_score(client, criteria, steps, response, metric_name):
    # Construct the evaluation prompt
    prompt = EVALUATION_PROMPT_TEMPLATE.format(
        criteria=criteria,
        steps=steps,
        document=response,  # In this case, the document is the response itself
        summary=response,   # Using response as both the document and summary for evaluation
        metric_name=metric_name,
    )

    # Call OpenAI API to evaluate
    try:
        api_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return api_response.choices[0].message.content
    except Exception as e:
        # Handle exceptions (e.g., API errors) and possibly log them
        print(f"Error during evaluation: {e}")
        return "0"  # Return a default score in case of an error
