import streamlit as st
from evaluation_copilot.base import MODEL, EvaluationCopilot, RelevanceEvaluationCopilot, CoherenceEvaluationCopilot, FluencyEvaluationCopilot, GroundednessEvaluationCopilot, ImprovementCopilot
from evaluation_copilot.models import EvaluationInput, ImprovementInput
import openai
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

client = openai.Client()
client.api_key = ""

user_api_key = st.sidebar.text_input("Enter your OpenAI API Key:", value="", type="password")
if not user_api_key:
    st.error("Please enter your OpenAI API Key in the sidebar.")
else:
    client.api_key = user_api_key
    llm = OpenAI(api_token=user_api_key, model_name=MODEL)

eval_copilot = EvaluationCopilot(client, logging=True)
relevance_eval_copilot = RelevanceEvaluationCopilot(client, logging=True)
coherence_eval_copilot = CoherenceEvaluationCopilot(client, logging=True)
fluency_eval_copilot = FluencyEvaluationCopilot(client, logging=True)
groundedness_eval_copilot = GroundednessEvaluationCopilot(client, logging=True)
improvement_copilot = ImprovementCopilot(client, logging=True)

def get_llm_response(question: str) -> str:
    """
    Function to get the response from an LLM for a given question.
    """
    try:
        response = client.chat.completions.create(
                model=MODEL, messages=[{"role": "system", "content": question}]
            )
        generated_text = response.choices[0].message.content
        return generated_text
    except openai.error.OpenAIError as e:
        st.error(f"An error occurred while fetching the LLM response: {e}")
        return ""
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return ""


# Sidebar buttons for switching between functionalities
app_mode = st.sidebar.radio(
    "Choose the application mode:",
    ("Evaluation Playground", "EvaluationCopilot Usage")
)

if app_mode == "Evaluation Playground":
    st.title('Evaluation Copilot Demo')

    evaluation_type = st.radio(
        "Select Evaluation Type:",
        ('General', 'Relevance', 'Coherence', 'Fluency', 'Groundedness')
    )

    context = ""
    # The text area is displayed only if the evaluation type requires context
    if evaluation_type in ('Relevance', 'Groundedness'):
        context = st.text_area("Enter context for evaluation:", value="France is a country in Western Europe known for its cities, history, and landmarks.")

    question = st.text_input("Enter your question:", value="What is the capital of France?")

    submit_button = st.button("Submit", disabled=(client.api_key == ""))

    if submit_button:
        llm_answer = get_llm_response(question)
        st.write("## LLM Answer", unsafe_allow_html=True)
        st.info(llm_answer)

        eval_input = EvaluationInput(question=question, answer=llm_answer, context=context if context else None)

        # Evaluate the LLM response based on the selected evaluation type
        if evaluation_type == 'General':
            eval_output = eval_copilot.evaluate(eval_input)
        elif evaluation_type == 'Relevance':
            eval_output = relevance_eval_copilot.evaluate(eval_input)
        elif evaluation_type == 'Coherence':
            eval_output = coherence_eval_copilot.evaluate(eval_input)
        elif evaluation_type == 'Fluency':
            eval_output = fluency_eval_copilot.evaluate(eval_input)
        elif evaluation_type == 'Groundedness':
            eval_output = groundedness_eval_copilot.evaluate(eval_input)

        st.write("## Evaluation", unsafe_allow_html=True)
        st.success(f"Score: {eval_output.score}")
        st.write(f"Justification:\n{eval_output.justification}")

        # Suggest improvements
        improvement_input = ImprovementInput(question=question, answer=llm_answer, score=eval_output.score, justification=eval_output.justification, context=context if context else None)
        improvement_output = improvement_copilot.suggest_improvements(improvement_input)
        st.write("## Improvement Suggestions", unsafe_allow_html=True)
        if improvement_output.question_improvement:
            st.markdown("#### Question Improvement", unsafe_allow_html=True)
            st.markdown(f"> {improvement_output.question_improvement}", unsafe_allow_html=True)

        if improvement_output.answer_improvement:
            st.markdown("#### Answer Improvement", unsafe_allow_html=True)
            st.markdown(f"> {improvement_output.answer_improvement}", unsafe_allow_html=True)

elif app_mode == "EvaluationCopilot Usage":
    st.title("File Analyser with Pandas AI")
    uploaded_file = st.file_uploader("Upload a file for analysis", type=['xlsx', 'csv'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file, header=None, names=['id', 'questions', 'answers', 'scores', 'justifications'])
        sdf = SmartDataframe(df, config={'llm': llm})
        st.write(df.head())

        prompt = st.text_area("Enter Prompt")
        if st.button("Submit"):
            if prompt:
                st.write("PandasAI is generating answer...")
                print("Before")
                resp = sdf.chat(prompt, )
                print(resp)
                st.write(resp)
                print("after")
            else:
                st.warning("Please enter a prompt.")


# st.title('Evaluation Copilot Demo')

# evaluation_type = st.radio(
#     "Select Evaluation Type:",
#     ('General', 'Relevance', 'Coherence', 'Fluency', 'Groundedness')
# )

# context = ""
# # The text area is displayed only if the evaluation type requires context
# if evaluation_type in ('Relevance', 'Groundedness'):
#     context = st.text_area("Enter context for evaluation:", value="France is a country in Western Europe known for its cities, history, and landmarks.")

# question = st.text_input("Enter your question:", value="What is the capital of France?")

# submit_button = st.button("Submit", disabled=(client.api_key == ""))

# if submit_button:
#     llm_answer = get_llm_response(question)
#     st.write("## LLM Answer", unsafe_allow_html=True)
#     st.info(llm_answer)

#     eval_input = EvaluationInput(question=question, answer=llm_answer, context=context if context else None)

#     # Evaluate the LLM response based on the selected evaluation type
#     if evaluation_type == 'General':
#         eval_output = eval_copilot.evaluate(eval_input)
#     elif evaluation_type == 'Relevance':
#         eval_output = relevance_eval_copilot.evaluate(eval_input)
#     elif evaluation_type == 'Coherence':
#         eval_output = coherence_eval_copilot.evaluate(eval_input)
#     elif evaluation_type == 'Fluency':
#         eval_output = fluency_eval_copilot.evaluate(eval_input)
#     elif evaluation_type == 'Groundedness':
#         eval_output = groundedness_eval_copilot.evaluate(eval_input)

#     st.write("## Evaluation", unsafe_allow_html=True)
#     st.success(f"Score: {eval_output.score}")
#     st.write(f"Justification:\n{eval_output.justification}")

#     # Suggest improvements
#     improvement_input = ImprovementInput(question=question, answer=llm_answer, score=eval_output.score, justification=eval_output.justification, context=context if context else None)
#     improvement_output = improvement_copilot.suggest_improvements(improvement_input)
#     st.write("## Improvement Suggestions", unsafe_allow_html=True)
#     if improvement_output.question_improvement:
#         st.markdown("#### Question Improvement", unsafe_allow_html=True)
#         st.markdown(f"> {improvement_output.question_improvement}", unsafe_allow_html=True)

#     if improvement_output.answer_improvement:
#         st.markdown("#### Answer Improvement", unsafe_allow_html=True)
#         st.markdown(f"> {improvement_output.answer_improvement}", unsafe_allow_html=True)