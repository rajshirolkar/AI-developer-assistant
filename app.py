from enum import Enum
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from evaluation_copilot.models import EvaluationInput, EvaluationOutput, ImprovementOutput, ImprovementInput
from evaluation_copilot.base import MODEL, EvaluationCopilot, RelevanceEvaluationCopilot, CoherenceEvaluationCopilot, FluencyEvaluationCopilot, GroundednessEvaluationCopilot, ImprovementCopilot
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.Client()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluationType(str, Enum):
    general = "General"
    relevance = "Relevance"
    coherence = "Coherence"
    fluency = "Fluency"
    groundedness = "Groundedness"

class EvaluationRequest(EvaluationInput):
    evaluation_type: EvaluationType

class ImprovementRequest(EvaluationInput, EvaluationOutput):
    pass

class GetResponseInput(BaseModel):
    question: str

@app.post("/get_response")
async def get_response(input_data: GetResponseInput):
    try:
        response = client.chat.completions.create(
            model=MODEL, messages=[{"role": "system", "content": input_data.question}]
        )
        generated_text = response.choices[0].message.content
        return {"answer": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize the copilots
eval_copilot = EvaluationCopilot(logging=True)
relevance_eval_copilot = RelevanceEvaluationCopilot(logging=True)
coherence_eval_copilot = CoherenceEvaluationCopilot(logging=True)
fluency_eval_copilot = FluencyEvaluationCopilot(logging=True)
groundedness_eval_copilot = GroundednessEvaluationCopilot(logging=True)
improvement_copilot = ImprovementCopilot(logging=True)

@app.post("/evaluate_endpoint", response_model=EvaluationOutput)
async def evaluate_response(eval_request: EvaluationRequest):
    # Select the appropriate EvaluationCopilot based on the evaluation type
    if eval_request.evaluation_type == EvaluationType.general:
        copilot = eval_copilot
    elif eval_request.evaluation_type == EvaluationType.relevance:
        copilot = relevance_eval_copilot
    elif eval_request.evaluation_type == EvaluationType.coherence:
        copilot = coherence_eval_copilot
    elif eval_request.evaluation_type == EvaluationType.fluency:
        copilot = fluency_eval_copilot
    elif eval_request.evaluation_type == EvaluationType.groundedness:
        copilot = groundedness_eval_copilot
    else:
        raise HTTPException(status_code=400, detail="Invalid evaluation type")

    # Logic to evaluate the response based on the evaluation type, context, etc.
    evaluation_response = copilot.evaluate(eval_request)
    return evaluation_response

@app.post("/improvement_suggestions", response_model=ImprovementOutput)
async def get_improvement_suggestions(improvement_request: ImprovementRequest):
    # Logic to generate improvement suggestions based on the evaluation
    improvement_input = ImprovementInput(
        question=improvement_request.question,
        answer=improvement_request.answer,
        score=improvement_request.score,
        justification=improvement_request.justification,
        context=improvement_request.context
    )
    improvement_response = improvement_copilot.suggest_improvements(improvement_input)
    return improvement_response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="info", reload=True)