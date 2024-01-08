from evaluation_utils.azure.azure_eval_criteria import COHERENCE_PROMPT_TEMPLATE, FLUENCY_PROMPT_TEMPLATE


def get_eval_score(client, user_prompt, response, prompt_template):
    prefix_prompt = prompt_template.format(
        question=user_prompt,
        answer=response,
    )
    print(prefix_prompt)

    # Call OpenAI API to evaluate
    try:
        api_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prefix_prompt}]
        )
        return api_response.choices[0].message.content
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return "0"


def azure_evaluation(user_prompt, response_text, client):
    scores = {
        # "Relevance": RELEVANCE_PROMPT_TEMPLATE,
        "Coherence": COHERENCE_PROMPT_TEMPLATE,
        "Fluency": FLUENCY_PROMPT_TEMPLATE,
    }
    for eval_type, prompt_template in scores.items():
        score = get_eval_score(client, user_prompt, response_text, prompt_template)
        scores[eval_type] = score.strip()

    return scores
