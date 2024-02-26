from pydantic import BaseModel


class Question(BaseModel):
    question: str

class EvaluationInput(BaseModel):
    question: str
    answer: str

class EvaluationOutput(BaseModel):
    score: int
    justification: str

class ImprovementInput(EvaluationInput, EvaluationOutput):
    pass

class ImprovementOutput(BaseModel):
    question_improvement: str
    answer_improvement: str