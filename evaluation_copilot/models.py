from pydantic import BaseModel
from typing import Optional

class Question(BaseModel):
    question: str

class EvaluationInput(BaseModel):
    question: str
    answer: str
    context: Optional[str] = None  # Optional field for reference text

class EvaluationOutput(BaseModel):
    score: int
    justification: str

class ImprovementInput(EvaluationInput, EvaluationOutput):
    pass

class ImprovementOutput(BaseModel):
    question_improvement: str
    answer_improvement: str