from evaluation_copilot.models import EvaluationInput, EvaluationOutput, ImprovementInput, ImprovementOutput 
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

evaluation_system_prompt_with_context_template = """
    [System]
    Please act as an impartial judge and evaluate the quality of the response provided by an
    AI assistant to the user question displayed below, considering the provided context as the ground truth. Your evaluation should consider factors
    such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of
    the response in relation to the context that was used to give the answer. Begin your evaluation by providing a short explanation. Be as objective and concise as
    possible using simple language. The explanation should be 2-3 bullet points that are easy to glance over. After providing your explanation, please rate the response on a scale of 1 to 5
    by strictly following this format: "[[explanation]],  [[rating]]", 
    for example: "Explanation:[[explanation..]], Rating: [[5]]".
    [Context]
    {context}
    [Question]
    {question}
    [The Start of Assistant’s Answer]
    {answer}
    [The End of Assistant’s Answer]
"""

class EvaluationCopilot:
    def __init__(self, client, logging=False, use_context=False):
        self.client = client
        self.logging_enabled = logging
        self.use_context = use_context  # Store the flag indicating if context should be used
        # Choose the appropriate template based on whether context is used
        if use_context:
            self.prompt_template = evaluation_system_prompt_with_context_template
        else:
            self.prompt_template = evaluation_system_prompt_template

    def log(self, message):
        if self.logging_enabled:
            print(message)

    def evaluate(self, eval_input: EvaluationInput) -> EvaluationOutput:
        # Check if context is required and if it's missing
        if self.use_context and (not hasattr(eval_input, 'context') or eval_input.context is None):
            raise ValueError("Context is required for evaluation but was not provided.")

        # Adjust the prompt formatting based on whether context is provided
        if self.use_context:
            prompt = self.prompt_template.format(context=eval_input.context, question=eval_input.question, answer=eval_input.answer)
        else:
            prompt = self.prompt_template.format(question=eval_input.question, answer=eval_input.answer)
        self.log(f"Prompt: {prompt}")
        response_text = self.chat_complete(prompt)
        rating, explanation = self.parse_response(response_text)
        score = int(rating.strip())
        evaluation_output = EvaluationOutput(score=score, justification=explanation)
        return evaluation_output
    
    def chat_complete(self, prompt):
        response = self.client.chat.completions.create(
                model=MODEL, messages=[{"role": "system", "content": prompt}]
            )
        generated_text = response.choices[0].message.content
        return generated_text

    def parse_response(self, response_text):
        explanation = response_text.split("Explanation:")[1].split("Rating:")[0].replace("[[", "").replace("]]", "")
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

improvement_system_prompt_with_context_template = """
[System]
You are an expert in assessing AI Question Answer evaluation report. You will be given a short evaluation report of an AI response to a user question, considering the provided context as the ground truth. The evaluation report gives you a score the QA pair received and an explanation of why a certain score was given. 
Based on the evaluation report and the context, you will be required to provide suggestions on some improvements that can be made to the user's question, the AI's response, and how the context could better inform the answer.
Be as objective as possible and your suggestions should be actionable items in 2-3 bullets that can be quickly glanced over. 
Give your suggestions by strictly following this format: "Question Improvement: [[question improvement suggestion..]], Answer Improvement: [[answer improvement suggestion..]]".

[The Start of Evaluation Report]

[Context]
{context}

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
    def __init__(self, client, logging=False, use_context=False):
        self.client = client
        self.logging_enabled = logging
        self.use_context = use_context
        if use_context:
            self.prompt_template = improvement_system_prompt_with_context_template
        else:
            self.prompt_template = improvement_system_prompt_template

    def log(self, message):
        if self.logging_enabled:
            print(message)
    
    def suggest_improvements(self, improvement_input: ImprovementInput):
        # Check if context is required and if it's missing
        if self.use_context and (not hasattr(improvement_input, 'context') or improvement_input.context is None):
            raise ValueError("Context is required for improvement suggestions but was not provided.")

        # Adjust the prompt formatting based on whether context is provided
        if self.use_context:
            prompt = self.prompt_template.format(
                context=improvement_input.context, 
                question=improvement_input.question, 
                answer=improvement_input.answer, 
                score=improvement_input.score, 
                explanation=improvement_input.justification
            )
        else:
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
        response =self.client.chat.completions.create(
                model=MODEL, messages=[{"role": "system", "content": prompt}]
            )
        generated_text = response.choices[0].message.content
        return generated_text




relevance_evaluation_prompt_template = """
    [System]
    Please focus specifically on evaluating the relevance of the AI assistant's response to the user's question, considering the provided context as the ground truth. 
    Assess whether the response directly addresses the question and is grounded in the context provided. 
    Begin your evaluation by providing a short explanation focused on the relevance aspect. 
    Be as objective and concise as possible using simple language. The explanation should be 2-3 bullet points that are easy to glance over. 
    After providing your explanation, please rate the response on a scale of 1 to 5
    by strictly following this format: "[[explanation]],  [[rating]]", 
    for example: "Explanation:[[explanation..]], Rating: [[5]]".
    [Context]
    {context}
    [Question]
    {question}
    [The Start of Assistant’s Answer]
    {answer}
    [The End of Assistant’s Answer]
"""

class RelevanceEvaluationCopilot(EvaluationCopilot):
    def __init__(self, client, logging=False):
        super().__init__(client, logging=logging, use_context=True)
        self.prompt_template = relevance_evaluation_prompt_template


coherence_evaluation_prompt_template = """
    [System]
    Please focus specifically on evaluating the coherence of the AI assistant's response to the user's question{context_clause}. 
    Assess whether the response is logically structured, clear, and maintains a consistent focus throughout, effectively addressing the user's question. 
    Begin your evaluation by providing a short explanation focused on the coherence aspect. 
    Be as objective and concise as possible using simple language. The explanation should be 2-3 bullet points that are easy to glance over. 
    After providing your explanation, please rate the response on a scale of 1 to 5
    by strictly following this format: "[[explanation]],  [[rating]]", 
    for example: "Explanation:[[explanation..]], Rating: [[5]]".
    {context_section}
    [Question]
    {question}
    [The Start of Assistant’s Answer]
    {answer}
    [The End of Assistant’s Answer]
"""

class CoherenceEvaluationCopilot(EvaluationCopilot):
    def __init__(self,client, logging=False, use_context=True):
        super().__init__(client, logging=logging, use_context=use_context)
        self.prompt_template = coherence_evaluation_prompt_template

    def evaluate(self, eval_input: EvaluationInput) -> EvaluationOutput:
        context_clause = ", considering the provided context as the ground truth" if self.use_context else ""
        context_section = "[Context]\n    {context}\n" if self.use_context and hasattr(eval_input, 'context') and eval_input.context is not None else ""
        # Adjust the prompt formatting based on whether context is provided
        prompt = self.prompt_template.format(
            context_clause=context_clause,
            context_section=context_section,
            question=eval_input.question,
            answer=eval_input.answer
        )
        self.log(f"Prompt: {prompt}")
        response_text = self.chat_complete(prompt)
        rating, explanation = self.parse_response(response_text)
        score = int(rating.strip())
        evaluation_output = EvaluationOutput(score=score, justification=explanation)
        return evaluation_output


groundedness_evaluation_prompt_template = """
    [System]
    Please focus specifically on evaluating the groundedness of the AI assistant's response to the user's question, ensuring that the response is well-grounded in the provided context. 
    Assess whether the response accurately reflects the information in the context, and if it uses the context to inform and support the answer effectively. 
    Begin your evaluation by providing a short explanation focused on the groundedness aspect. 
    Be as objective and concise as possible using simple language. The explanation should be 2-3 bullet points that are easy to glance over. 
    After providing your explanation, please rate the response on a scale of 1 to 5
    by strictly following this format: "[[explanation]],  [[rating]]", 
    for example: "Explanation:[[explanation..]], Rating: [[5]]".
    [Context]
    {context}
    [Question]
    {question}
    [The Start of Assistant’s Answer]
    {answer}
    [The End of Assistant’s Answer]
"""

class GroundednessEvaluationCopilot(EvaluationCopilot):
    def __init__(self,client, logging=False):
        # For GroundednessEvaluation, use_context is always True
        super().__init__(client, logging=logging, use_context=True)
        self.prompt_template = groundedness_evaluation_prompt_template

    def evaluate(self, eval_input: EvaluationInput) -> EvaluationOutput:
        if not hasattr(eval_input, 'context') or eval_input.context is None:
            raise ValueError("Context is required for groundedness evaluation but was not provided.")
        
        prompt = self.prompt_template.format(
            context=eval_input.context,
            question=eval_input.question,
            answer=eval_input.answer
        )
        self.log(f"Prompt: {prompt}")
        response_text = self.chat_complete(prompt)
        rating, explanation = self.parse_response(response_text)
        score = int(rating.strip())
        evaluation_output = EvaluationOutput(score=score, justification=explanation)
        return evaluation_output


fluency_evaluation_prompt_template = """
    [System]
    Please focus specifically on evaluating the fluency of the AI assistant's response to the user's question. 
    Assess how well the generated text adheres to grammatical rules, syntactic structures, and appropriate usage of vocabulary, resulting in linguistically correct and natural-sounding responses. 
    Consider the quality of individual sentences and whether they are well-written and grammatically correct. 
    Begin your evaluation by providing a short explanation focused on the fluency aspect. 
    Be as objective and concise as possible using simple language. The explanation should be 2-3 bullet points that are easy to glance over. 
    After providing your explanation, please rate the response on a scale of 1 to 5
    by strictly following this format: "[[explanation]],  [[rating]]", 
    for example: "Explanation:[[explanation..]], Rating: [[5]]".
    [Question]
    {question}
    [The Start of Assistant’s Answer]
    {answer}
    [The End of Assistant’s Answer]
"""

class FluencyEvaluationCopilot(EvaluationCopilot):
    def __init__(self,client, logging=False):
        # For FluencyEvaluation, use_context is always False
        super().__init__(client, logging=logging, use_context=False)
        self.prompt_template = fluency_evaluation_prompt_template