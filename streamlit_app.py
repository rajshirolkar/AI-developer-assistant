import streamlit as st
from evaluation_copilot.base import MODEL, EvaluationCopilot, ImprovementCopilot
from evaluation_copilot.models import EvaluationInput, ImprovementInput
import openai

# Load your environment variables and set up OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.Client()
# Initialize the copilots
eval_copilot = EvaluationCopilot(logging=True)
improvement_copilot = ImprovementCopilot(logging=True)

def get_llm_response(question: str) -> str:
    """
    Function to get the response from an LLM for a given question.
    """
    response = client.chat.completions.create(
            model=MODEL, messages=[{"role": "system", "content": question}]
        )
    generated_text = response.choices[0].message.content
    return generated_text

st.title('LLM Evaluation and Improvement Suggestion Tool')

with st.form("llm_query"):
    question = st.text_input("Enter your question:", value="What is the capital of France?")
    submit_button = st.form_submit_button("Submit")

if submit_button:
    # Get the LLM response
    llm_answer = get_llm_response(question)
    st.write("## LLM Answer", unsafe_allow_html=True)
    st.info(llm_answer)

    # Evaluate the LLM response
    eval_input = EvaluationInput(question=question, answer=llm_answer)
    eval_output = eval_copilot.evaluate(eval_input)
    st.write("## Evaluation", unsafe_allow_html=True)
    st.success(f"Score: {eval_output.score}")
    st.write(f"Justification:\n{eval_output.justification}")

    # Suggest improvements
    improvement_input = ImprovementInput(question=question, answer=llm_answer, score=eval_output.score, justification=eval_output.justification)
    improvement_output = improvement_copilot.suggest_improvements(improvement_input)
    st.write("## Improvement Suggestions", unsafe_allow_html=True)
    st.warning(f"Question Improvement:\n{improvement_output.question_improvement}")
    st.warning(f"Answer Improvement:\n{improvement_output.answer_improvement}")