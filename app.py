from typing import Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.logger import logger
from fastapi.params import Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from evaluation_utils.azure.azure_eval_criteria import RELEVANCE_PROMPT_TEMPLATE
from evaluation_utils.eval_copilot import eval_copilot_log
import openai
import os
from dotenv import load_dotenv

from evaluation_utils.azure.azure_eval import azure_evaluation
from evaluation_utils.eval_copilot.copilot_eval_criteria import (
    evaluation_system_prompt,
    evaluation_instructions,
    improvement_user_instructions,
    improvement_system_content,
    example_improvement_suggestions,
    new_coherence_prompt,
)
from evaluation_utils.eval_copilot.copilot_utils import (
    create_message,
    run_chat_completions,
)
from evaluation_utils.eval_copilot.eval_copilot import (
    copilot_evaluation,
    EvaluationCopilot,
)
from evaluation_utils.eval_copilot.generic_evaluation import (
    get_generic_evaluation_score,
)
from evaluation_utils.eval_copilot.improvement_copilot import ImprovementCopilot
from evaluation_utils.eval_copilot.relevance_evaluation import (
    ImprovementCopilotNew,
    relevance_improvement_prompts,
)
from models.evaluation_models import CopilotEvaluationResponse, CopilotEvaluation
from models.prompt_models import GenerationResponse

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.Client()
templates = Jinja2Templates(directory="templates")
out_log = eval_copilot_log.eval_copilot_log()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("input_form.html", {"request": request})


class CoherenceEvaluation(BaseModel):
    coherence: int = Field(
        ge=1, le=5, description="Score for the coherence of the text"
    )
    justification: str = Field(..., description="Justification for the given score")
    improvement_suggestion: str = Field(
        ..., description="Suggested actionable improvement"
    )


ground_truth = """
Seasonal allergies affect 50 million Americans, causing symptoms like itchy, watery eyes, a tickly throat, and a stuffy, runny nose, which can be triggered by tree pollen, grass, mold, and ragweed. Allergies can lead to fatigue, making it difficult to distinguish them from colds. Yale Medicine allergists work to identify the causes of allergies and provide treatment for a range of allergic and immunologic disorders, including seasonal allergies, allergic sinusitis, chronic sinusitis, asthma, and allergies related to food and medications.
Allergies occur when the immune system overreacts to allergens, releasing chemicals that cause symptoms like congestion, sneezing, and itchy eyes. The severity of allergies can vary based on the perceived threat of the allergen. Common seasonal allergy symptoms include congestion, sneezing, itchy eyes, nose and throat, runny nose and eyes, post-nasal drip, fatigue, and coughing. Seasonal allergens peak at different times of the year, while perennial allergies can occur year-round.
To diagnose allergies, allergists may perform skin tests or blood tests. Treatment options include over-the-counter or prescription antihistamines, decongestants, cough medications, antihistamine or steroidal nose sprays, and allergen immunotherapy through subcutaneous injections or sublingual tablets.
To reduce exposure to allergens, individuals should monitor daily pollen and mold spore levels, start medications before allergy season, keep windows and doors shut, wear a hat outdoors, change clothes after being outside, and avoid activities that trigger allergies or wear a mask if necessary.
"""

system_prompt_ground_truth = """
You are a helpful assistant. You will be given a groundtruth and a prompt. Your job is to provide a response that is relevant to the groundtruth and prompt.

Ground Truth:
{ground_truth}
"""

improvement_copilot = ImprovementCopilotNew(relevance_improvement_prompts)


@app.post("/use-evaluation-copilot/", response_model=CoherenceEvaluation)
async def use_evaluation_copilot(request: Request, prompt: str = Form(...)):
    # Ensure the API key is set
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Generate the response from OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "system", "content": system_prompt_ground_truth.format(ground_truth=ground_truth)},
                                     {"role": "user", "content": prompt}]
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    azure_eval_msg = create_message(
        "system",
        RELEVANCE_PROMPT_TEMPLATE.format(
            context=ground_truth, question=prompt, answer=response
        ),
    )
    azure_eval_score_response = run_chat_completions([azure_eval_msg])
    azure_eval_score = azure_eval_score_response.split("tars:")[1].strip()

    (
        eval1_score,
        eval1_justification,
        eval1_improvement_suggestion,
    ) = improvement_copilot.get_improvement_suggestion(
        ground_truth, prompt, generated_text
    )
    generic_eval = get_generic_evaluation_score(prompt, generated_text, client)

    response_data = {
        "request": request,
        "prompt": prompt,
        "response": generated_text,
        "azure_evaluation_score": azure_eval_score,
        "score": eval1_score,
        "justification": eval1_justification,
        "improvement_suggestion": eval1_improvement_suggestion,
        "new_evaluation_score": generic_eval["rating"],
        "new_evaluation_justification": generic_eval["explanation"],
        "new_evaluation_improvement_suggestion": generic_eval[
            "improvement_suggestions"
        ],
    }
    print(response_data)
    out_log.add_line(response_data)
    return templates.TemplateResponse("input_form.html", response_data)


@app.post("/generate-and-score/", response_model=GenerationResponse)
async def generate_and_score(request: Request, prompt: str = Form(...)):
    # Ensure the API key is set
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print(request, prompt)

    # Generate the response from OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # scores = evaluate_response(generated_text, client)
    scores = azure_evaluation(prompt, generated_text, client)
    score_colors = {
        # "Relevance": "red" if int(scores['Relevance']) < 3 else "green",
        "Coherence": "red" if int(scores["Coherence"]) < 3 else "green",
        # "Consistency": "red" if int(scores['Consistency']) < 3 else "green",
        "Fluency": "red" if int(scores["Fluency"]) < 3 else "green",
    }

    response_data = {
        "request": request,
        "prompt": prompt,
        "response": generated_text,
        "scores": scores,
        "score_colors": score_colors,
    }
    return templates.TemplateResponse("input_form.html", response_data)


@app.post("/eval-copilot", response_model=CopilotEvaluationResponse)
async def eval_copilot(request: Request, prompt: str = Form(...)):
    # Generate the response from OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": prompt}]
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error during OpenAI API call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # Implement your new evaluation logic here
    # For example, you can call a function that performs the evaluation and returns the score, justification, and improvement suggestion
    evaluations = copilot_evaluation(prompt, generated_text, client)
    print("Evaluations:", evaluations)

    evaluation_data = CopilotEvaluationResponse(
        prompt=prompt,
        response=generated_text,
        evaluation=CopilotEvaluation(
            score=evaluations["Coherence"]["score"],
            justification=evaluations["Coherence"]["justification"],
            improvement_suggestion=evaluations["Coherence"]["improvement_suggestion"],
        ),
    )
    return evaluation_data

class ThumbClick(BaseModel):
    intVariable: int
@app.post('/thumb_click')
async def thumb_click(clickInfo: ThumbClick):
    button_number = clickInfo.intVariable
    out_log.add_thumb(str(button_number))
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import uvicorn

    out_log = eval_copilot_log.eval_copilot_log()

    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="info")
