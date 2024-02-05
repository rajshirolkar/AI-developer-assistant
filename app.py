from typing import Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.logger import logger
from fastapi.params import Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
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
from evaluation_utils.eval_copilot.eval_copilot import (
    copilot_evaluation,
    EvaluationCopilot,
)
from evaluation_utils.eval_copilot.improvement_copilot import ImprovementCopilot
from models.evaluation_models import CopilotEvaluationResponse, CopilotEvaluation
from models.prompt_models import GenerationResponse

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.Client()
templates = Jinja2Templates(directory="templates")
out_log = eval_copilot_log.eval_copilot_log()
app = FastAPI()


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


improvement_copilot = ImprovementCopilot(
    improvement_instructions=improvement_user_instructions,
    improvement_system_prompt=improvement_system_content,
    evaluation_instructions=evaluation_instructions,
    evaluation_system_prompt=evaluation_system_prompt,
    few_shot_examples=example_improvement_suggestions,
)

new_evaluation = EvaluationCopilot(new_coherence_prompt)


@app.post("/use-evaluation-copilot/", response_model=CoherenceEvaluation)
async def use_evaluation_copilot(request: Request, prompt: str = Form(...)):
    # Ensure the API key is set
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Generate the response from OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    (
        coherence,
        justification,
        improvement_suggestion,
    ) = improvement_copilot.get_improvement_suggestion(prompt, generated_text)

    print("Coherence:", coherence)
    (
        new_evaluation_score,
        new_evaluation_justification,
    ) = new_evaluation.get_score_and_justification(prompt, generated_text)
    response_data = {
        "request": request,
        "prompt": prompt,
        "response": generated_text,
        "coherence": coherence,
        "justification": justification,
        "improvement_suggestion": improvement_suggestion,
        "new_evaluation_score": new_evaluation_score,
        "new_evaluation_justification": new_evaluation_justification,
    }
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


if __name__ == "__main__":
    import uvicorn
    out_log=eval_copilot_log.eval_copilot_log()


    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
