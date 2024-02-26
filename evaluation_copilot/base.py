import openai
import os
from dotenv import load_dotenv
from models import EvaluationInput, EvaluationOutput, ImprovementInput, ImprovementOutput  # Import the necessary models

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.Client()
MODEL = "gpt-4-1106-preview"


evaluation_system_prompt_template = """
    [System]
    Please act as an impartial judge and evaluate the quality of the response provided by an
    AI assistant to the user question displayed below. Your evaluation should consider factors
    such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of
    the response. Begin your evaluation by providing a short explanation. Be as objective and concise as
    possible using simple language. The explanation should be 2-3 bullet points that are easy to glance over. After providing your explanation, please rate the response on a scale of 1 to 5
    by strictly following this format: "[[explanation]],  [[rating]]", 
    for example: "Explanation:[[explanation..]], Rating: [[5]]".
    [Question]
    {question}
    [The Start of Assistant’s Answer]
    {answer}
    [The End of Assistant’s Answer]
"""

class EvaluationCopilot:
    def __init__(self, logging=False, prompt_template=evaluation_system_prompt_template):
        self.prompt_template = prompt_template
        self.logging_enabled = logging

    def log(self, message):
        if self.logging_enabled:
            print(message)

    def evaluate(self, eval_input: EvaluationInput) -> EvaluationOutput:

        prompt = self.prompt_template.format(question=eval_input.question, answer=eval_input.answer)
        response_text = self.chat_complete(prompt)
        rating, explanation = self.parse_response(response_text)
        score = int(rating.strip())
        evaluation_output = EvaluationOutput(score=score, justification=explanation)
        return evaluation_output
    
    def chat_complete(self, prompt):
        response = client.chat.completions.create(
                model=MODEL, messages=[{"role": "system", "content": prompt}]
            )
        generated_text = response.choices[0].message.content
        return generated_text

    def parse_response(self, response_text):
        explanation = response_text.split("Explanation:")[1].split("Rating:")[0]
        rating = response_text.split("Rating:")[1].replace("[[", "").replace("]]", "")
        
        self.log(f"Parse Response - Explanation: {explanation.strip()}")
        self.log(f"Parse Response - Rating: {rating.strip()}")

        return rating, explanation


improvement_system_prompt_template = """
[System]
You are an expert in assessing AI Question Answer evaluation report. You will be given a short evaluation report of an AI response to a user question, with an
evaluation report giving you a score the QA pair received and an explanation of why a certain score was given. 
Based on the evaluation report, you will be required to provide suggestions on some improvements that can be made to the user's question and the AI's response.
Be as objective as possible and your suggestions should be actionable items in 2-3 bullets that can be quickly glanced over. 
Give your suggestions by strictly following this format: [[ question improvement suggestion ]], [[ answer improvement suggestion]].,
for example "Question Improvement: [[question improvement suggestion..]], Answer Improvement: [[answer improvement suggestion..]]".

[The Start of Evaluation Report]

[User's Question]
{question}

[The Start of Assistant’s Answer]
{answer}
[The End of Assistant’s Answer]

[Score]
{score}

[The Start of Explanation]
{explanation}
[The End of Explanation]

[The End of Evaluation Report]
"""


class ImprovementCopilot:
    def __init__(self, logging=False, prompt_template=improvement_system_prompt_template):
        self.prompt_template = prompt_template
        self.logging_enabled = logging

    def log(self, message):
        if self.logging_enabled:
            print(message)
    
    def suggest_improvements(self, improvement_input: ImprovementInput):
        prompt = self.prompt_template.format(
            question=improvement_input.question, 
            answer=improvement_input.answer, 
            score=improvement_input.score, 
            explanation=improvement_input.justification
        )

        response_text = self.chat_complete(prompt)
        improvement_output = self.parse_improvement_response(response_text)
        return improvement_output

    def parse_improvement_response(self, response_text):
        question_improvement = response_text.split("Question Improvement:")[1].split("Answer Improvement:")[0].strip()
        answer_improvement = response_text.split("Answer Improvement:")[1].strip()

        # Remove [[ and ]] from the improvement responses
        question_improvement = question_improvement.replace("[[", "").replace("]]", "").strip()
        answer_improvement = answer_improvement.replace("[[", "").replace("]]", "").strip()

        self.log(f"Parse Improvement Response - Question Improvement: {question_improvement}")
        self.log(f"Parse Improvement Response - Answer Improvement: {answer_improvement}")

        return ImprovementOutput(question_improvement=question_improvement, answer_improvement=answer_improvement)

    def chat_complete(self, prompt):
        response = client.chat.completions.create(
                model=MODEL, messages=[{"role": "system", "content": prompt}]
            )
        generated_text = response.choices[0].message.content
        return generated_text







# Initialize the EvaluationCopilot
eval_copilot = EvaluationCopilot()

# Create an EvaluationInput instance
eval_input = EvaluationInput(question="What is the capital of France?", answer="The capital of France is Paris.")

# Use the EvaluationCopilot to evaluate the input
eval_output = eval_copilot.evaluate(eval_input)

print(f"Score: {eval_output.score}\nJustification: {eval_output.justification}")

# Initialize the ImprovementCopilot
improvement_copilot = ImprovementCopilot()

# Create an ImprovementInput instance using the output from the evaluation
improvement_input = ImprovementInput(question=eval_input.question, 
                                     answer=eval_input.answer, 
                                     score=eval_output.score, 
                                     justification=eval_output.justification)

# Use the ImprovementCopilot to suggest improvements
improvement_output = improvement_copilot.suggest_improvements(improvement_input)

print(f"Question Improvement: {improvement_output.question_improvement}\nAnswer Improvement: {improvement_output.answer_improvement}")