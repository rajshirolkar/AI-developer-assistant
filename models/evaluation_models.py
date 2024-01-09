from pydantic import BaseModel, Field


class CopilotEvaluation(BaseModel):
    score: int = Field(ge=1, le=5, description="Evaluation score")
    justification: str = Field(..., description="Justification for the given score")
    improvement_suggestion: str = Field(..., description="Suggested actionable improvement")


class CopilotEvaluationResponse(BaseModel):
    prompt: str = Field(..., description="The original prompt text")
    response: str = Field(..., description="The generated text response from OpenAI")
    evaluation: CopilotEvaluation = Field(..., description="Copilot evaluation details")


class EvaluationScores(BaseModel):
    Relevance: int = Field(ge=1, le=5, description="Score for the relevance of the text")
    Coherence: int = Field(ge=1, le=5, description="Score for the coherence of the text")
    Consistency: int = Field(ge=1, le=5, description="Score for the consistency of the text")
    Fluency: int = Field(ge=1, le=5, description="Score for the fluency of the text")
