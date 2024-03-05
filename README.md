# Evaluation Copilot

## Overview

Evaluation Copilot is a comprehensive library designed to enhance the quality of Question and Answer (QnA) pairs through detailed evaluation and actionable improvement suggestions. Leveraging the capabilities of Large Language Models (LLMs), this library aims to provide insightful feedback on QnA pairs, focusing on aspects such as relevance, coherence, fluency, and groundedness. The library is divided into two main components:

1. **Evaluation:** This component assigns a score to each QnA pair, accompanied by a justification that sheds light on the reasoning behind the score. The objective is to uncover the evaluative criteria of the LLM, offering a transparent and grounded explanation for the assessment.
2. **Improvement Suggestions:** Based on the evaluation's outcome, the ImprovementCopilot suggests concrete steps to refine both the question and the answer. This feature is invaluable for developers seeking to optimize datasets and guide the system towards desired performance benchmarks.

## Features

- **Comprehensive Evaluation:** Assess QnA pairs on multiple dimensions including relevance, coherence, fluency, and groundedness.
- **Actionable Improvements:** Receive specific suggestions to enhance the quality of both questions and answers.
- **Context-Aware Analysis:** Incorporate contextual information for a more nuanced evaluation of relevance and groundedness.
- **Extensible Framework:** Easily extend the EvaluationCopilot class to create custom evaluations tailored to specific needs.

# Getting Started

## Installation

Before installing the required packages, it is recommended to create a virtual environment:

### Creating a Virtual Environment

On macOS and Linux:

```bash
python3 -m venv venv
```

On Windows:

```bash
python -m venv venv
```

### Activating the Virtual Environment

Activate the virtual environment before installing dependencies and running the application.

On macOS and Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
.\venv\Scripts\activate
```

### Install Dependencies

With the virtual environment activated, install the necessary packages using:

```bash
pip install -r requirements.txt
```

## Setting Up Your Environment

1. Clone the repository to your local machine.
2. Navigate to the repository directory.
3. If you haven't already, activate your virtual environment.
4. Create a `.env` file in the root of the project to store your OpenAI API key securely:

```dotenv
# .env file
OPENAI_API_KEY='your-api-key-here'
```

## Running the Application with Streamlit

Streamlit is an open-source app framework that is perfect for building and sharing data applications. To run the Evaluation Copilot application using Streamlit, follow these steps:


### Starting the Streamlit Application

Navigate to the directory containing your Streamlit script (`streamlit_app.py` in this case). You can start the Streamlit server by running:

```bash
streamlit run streamlit_app.py
```

This command will start the Streamlit server and open your default web browser to the URL where the app is being served, typically `http://localhost:8501`.

### Using the Application

Once the Streamlit application is running, you can interact with it through the web interface. The application's UI will guide you through the following steps:

1. **Select Evaluation Type:** Choose the type of evaluation you want to perform (e.g., General, Relevance, Coherence, Fluency, Groundedness).
2. **Enter Context (if required):** For evaluations that require context (e.g., Relevance, Groundedness), a text area will be provided to enter the context.
3. **Enter Your Question:** Input the question you want to evaluate in the provided text input field.
4. **Submit for Evaluation:** Click the "Submit" button to send your input to the Evaluation Copilot for processing.

### Basic Usage

#### Evaluation

To perform an evaluation, import `EvaluationInput` and `EvaluationCopilot`, and initialize the `EvaluationCopilot` with logging enabled for verbose output. Create an `EvaluationInput` instance with the question and answer, and call the evaluate method.

```python
from evaluation_copilot.base import EvaluationCopilot, EvaluationInput

eval_copilot = EvaluationCopilot(logging=True)
eval_input = EvaluationInput(question="What is the capital of France?", answer="Paris")
eval_output = eval_copilot.evaluate(eval_input)

print(f"Score: {eval_output.score}, Justification: {eval_output.justification}")
```

#### Improvement Suggestions

To obtain improvement suggestions, initialize `ImprovementCopilot` with the evaluation input and output. The `suggest_improvements` method will return actionable feedback for both the question and the answer.

```python
from evaluation_copilot.base import ImprovementCopilot, ImprovementInput

improvement_copilot = ImprovementCopilot(logging=True)
improvement_input = ImprovementInput(question="What is the capital of France?", answer="Paris", score=eval_output.score, justification=eval_output.justification)
improvement_output = improvement_copilot.suggest_improvements(improvement_input)

print(f"Question Improvement: {improvement_output.question_improvement}")
print(f"Answer Improvement: {improvement_output.answer_improvement}")
```

# Extending Evaluation Copilot

Evaluation Copilot is designed to be an extensible framework, allowing users to tailor the evaluation process to their specific needs. This flexibility is achieved through subclassing the base `EvaluationCopilot` class to create custom evaluation strategies. Below, we illustrate how to extend the library with a custom evaluation for relevance, including how to handle evaluations that require context.

## Custom Evaluation Example: Relevance Evaluation

To create a custom evaluation for assessing the relevance of an AI assistant's response to a user's question, you can subclass the `EvaluationCopilot` class. In this example, we focus on evaluating the relevance of the response, considering the provided context as the ground truth.

### Step 1: Define the Custom Evaluation Class

First, define your custom evaluation class by subclassing `EvaluationCopilot`. Override the `__init__` method to specify your custom prompt template and indicate whether the evaluation requires context.

```python
from evaluation_copilot.base import EvaluationCopilot

class RelevanceEvaluationCopilot(EvaluationCopilot):
    def __init__(self, logging=False):
        super().__init__(logging=logging, use_context=True)
        self.prompt_template = """
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
```

### Step 2: Use the Custom Evaluation Class

To use your custom evaluation class, simply instantiate it and call the `evaluate` method with an `EvaluationInput` instance that includes the necessary context, question, and answer.

```python
from evaluation_copilot.base import EvaluationInput, RelevanceEvaluationCopilot

# Initialize the custom evaluator with logging enabled
relevance_evaluator = RelevanceEvaluationCopilot(logging=True)

# Prepare the evaluation input, including the context
eval_input = EvaluationInput(
    context="France is a country in Western Europe known for its cities, history, and landmarks.",
    question="What is the capital of France?",
    answer="The capital of France is Paris."
)

# Perform the evaluation
eval_output = relevance_evaluator.evaluate(eval_input)

# Display the evaluation results
print(f"Score: {eval_output.score}, Justification: {eval_output.justification}")
```

### Handling Context in Evaluations

When your evaluation requires context (as in the relevance evaluation example), ensure that the `use_context` flag is set to `True` in the custom class's `__init__` method. This flag instructs the evaluation process to expect and incorporate context into the evaluation. When creating an `EvaluationInput` instance, include the context alongside the question and answer.

This example demonstrates how to extend Evaluation Copilot with custom evaluation logic, enabling you to tailor the evaluation process to meet diverse requirements and contexts.

## Contributing

Contributions are welcome! Whether it's extending the library with new features, improving documentation, or reporting issues, your input is highly valued. Please refer to the project's contribution guidelines for more information.

## License

Evaluation Copilot is released under [MIT License](LICENSE). Feel free to use, modify, and distribute the code as per the license agreement.