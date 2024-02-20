document.getElementById("sendPrompt").addEventListener("click", function () {
  const prompt = document.getElementById("promptInput").value;

  document.getElementById("loadingSpinnerResponse").style.display = "block";
  fetch("http://localhost:8000/your_endpoint", {
    // Adjust the URL to your FastAPI endpoint
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt: prompt }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("responseOutput").innerText = data.response;
    })
    .catch((error) => {
      console.error("Error:", error);
    })
    .finally(() => {
      // Hide the spinner
      document.getElementById("loadingSpinnerResponse").style.display = "none";
    });
});

document
  .getElementById("evaluateResponse")
  .addEventListener("click", function () {
    const prompt = document.getElementById("promptInput").value;
    const response = document.getElementById("responseOutput").innerText;
    document.getElementById("loadingSpinnerEvaluation").style.display = "block";

    fetch("http://localhost:8000/evaluate_endpoint", {
      // Adjust the URL to your FastAPI evaluate endpoint
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt: prompt, llm_response: response }),
    })
      .then((response) => response.json())
      .then((data) => {
        document.getElementById("evaluationScore").innerText =
          "Score: " + data.score;
        document.getElementById("evaluationJustification").innerText =
          "Justification: " + data.justification;
      })
      .catch((error) => {
        console.error("Error:", error);
      })
      .finally(() => {
        // Hide the spinner
        document.getElementById("loadingSpinnerEvaluation").style.display =
          "none";
      });
  });

document
  .getElementById("improvementSuggestions")
  .addEventListener("click", function () {
    const prompt = document.getElementById("promptInput").value;
    const response = document.getElementById("responseOutput").innerText;
    const score = document
      .getElementById("evaluationScore")
      .innerText.replace("Score: ", "");
    const justification = document
      .getElementById("evaluationJustification")
      .innerText.replace("Justification: ", "");

    console.log(prompt, response, score, justification);

    document.getElementById("loadingSpinnerImprovement").style.display =
      "block";

    fetch("http://localhost:8000/improvement_suggestions", {
      // Adjust the URL to your FastAPI improvement suggestions endpoint
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt: prompt,
        llm_response: response,
        rating: parseInt(score, 10),
        justification: justification,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        document.getElementById("questionImprovement").innerText =
          data.question_improvement;
        document.getElementById("answerImprovement").innerText =
          data.answer_improvement;
      })
      .catch((error) => {
        console.error("Error:", error);
      })
      .finally(() => {
        // Hide the spinner
        document.getElementById("loadingSpinnerImprovement").style.display =
          "none";
      });
  });
