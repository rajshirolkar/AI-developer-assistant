from evaluation import chat_complete, parse_response, parse_improvement_response, evaluation_system_prompt_template,improvement_system_prompt_template
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

class EvaluationRequest(BaseModel):
    prompt: str
    llm_response: str

class ImprovementRequest(BaseModel):
    prompt: str
    llm_response: str
    rating: int
    justification: str


@app.post("/your_endpoint")
async def get_response(prompt: Prompt):
    # Logic to generate a response

    generated_text = chat_complete(prompt.prompt)

    return {"response": generated_text}

@app.post("/evaluate_endpoint")
async def evaluate_response(eval_request: EvaluationRequest):
    # Logic to evaluate the response
    evaluation_system_prompt = evaluation_system_prompt_template.format(question=eval_request.prompt, 
                                                                        answer=eval_request.llm_response)

    evaluation_response = chat_complete(evaluation_system_prompt)

    explanation, improvement_suggestions, rating = parse_response(evaluation_response)

    print("Explanation : ", explanation)
    print("Improvement Suggestions : ", improvement_suggestions)
    print("Rating : ", rating)
    return {"score": rating, "justification": explanation}


@app.post("/improvement_suggestions")
async def get_improvement_suggestions(improvement_request: ImprovementRequest):
    # Logic to generate improvement suggestions
    improvement_system_prompt = improvement_system_prompt_template.format(question=improvement_request.prompt, 
                                                                          answer=improvement_request.llm_response, 
                                                                          score=improvement_request.rating, 
                                                                          explanation=improvement_request.justification)

    improvement_response = chat_complete(improvement_system_prompt)

    question_improvement, answer_improvement = parse_improvement_response(improvement_response)


    return {"question_improvement": question_improvement,
            "answer_improvement": answer_improvement}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="info", reload=True)

