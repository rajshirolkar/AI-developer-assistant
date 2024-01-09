from typing import Dict

from pydantic import BaseModel, Field

from models.evaluation_models import EvaluationScores


class Prompt(BaseModel):
    text: str


class GenerationResponse(BaseModel):
    prompt: str = Field(..., description="The original prompt text")
    response: str = Field(..., description="The generated text response from OpenAI")
    scores: EvaluationScores = Field(..., description="Evaluation scores for the generated text")
    score_colors: Dict[str, str] = Field(..., description="Color coding for the scores")
