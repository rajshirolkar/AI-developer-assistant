from typing import Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.params import Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3
from pydantic import BaseModel, Field
import openai
import os
from dotenv import load_dotenv

from evaluation_utils.eval import evaluate_response

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.Client()
templates = Jinja2Templates(directory="templates")

app = FastAPI()

class EvaluationScores(BaseModel):
    Relevance: int = Field(ge=1, le=5, description="Score for the relevance of the text")
    Coherence: int = Field(ge=1, le=5, description="Score for the coherence of the text")
    Consistency: int = Field(ge=1, le=5, description="Score for the consistency of the text")
    Fluency: int = Field(ge=1, le=5, description="Score for the fluency of the text")

class GenerationResponse(BaseModel):
    prompt: str = Field(..., description="The original prompt text")
    response: str = Field(..., description="The generated text response from OpenAI")
    scores: EvaluationScores = Field(..., description="Evaluation scores for the generated text")
    score_colors: Dict[str, str] = Field(..., description="Color coding for the scores")

class Prompt(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("input_form.html", {"request": request})


@app.post("/generate-and-score/", response_model=GenerationResponse)
async def generate_and_score(request: Request, prompt: str = Form(...)):
    # Ensure the API key is set
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print(request, prompt)

    # Generate the response from OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Evaluate the response (implement your evaluation logic here)
    scores = evaluate_response(generated_text, client)

    score_colors = {
        "Relevance": "red" if int(scores['Relevance']) < 3 else "green",
        "Coherence": "red" if int(scores['Coherence']) < 3 else "green",
        "Consistency": "red" if int(scores['Consistency']) < 3 else "green",
        "Fluency": "red" if int(scores['Fluency']) < 3 else "green",
    }

    response_data = {
        "request": request,
        "response": generated_text,
        "scores": scores,
        "score_colors": score_colors
    }
    return templates.TemplateResponse("input_form.html", response_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
