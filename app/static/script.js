document
  .getElementById("churnForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const resultBox = document.getElementById("result");

    resultBox.innerHTML = `
      <div class="result-box loading-box">
        <div class="loader"></div>
        <h3>Analyzing Customer...</h3>
        <p>Please wait while the model checks churn risk.</p>
      </div>
    `;

    resultBox.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    data.SeniorCitizen = Number(data.SeniorCitizen);
    data.tenure = Number(data.tenure);
    data.MonthlyCharges = Number(data.MonthlyCharges);
    data.TotalCharges = Number(data.TotalCharges);

    try {
      const response = await fetch("/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      await new Promise((resolve) => setTimeout(resolve, 2500));

      const probabilityPercent = (result.churn_probability * 100).toFixed(1);

      const resultClass =
        result.result === "Churn" ? "result-churn" : "result-no-churn";

      const message =
        result.result === "Churn"
          ? "This customer has a higher chance of leaving the service."
          : "This customer is less likely to leave the service.";

      resultBox.innerHTML = `
        <div class="result-box ${resultClass}">
          <p>Prediction</p>
          <h3>${result.result}</h3>
          <p>${message}</p>
          <div class="probability">${probabilityPercent}%</div>
          <p>Churn Probability</p>
        </div>

        <div class="note">
          Model can make mistakes. Use this prediction as a decision-support tool, not as the final decision.
        </div>
      `;

      resultBox.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    } catch (error) {
      await new Promise((resolve) => setTimeout(resolve, 1500));

      resultBox.innerHTML = `
        <div class="result-box result-churn">
          <h3>Error</h3>
          <p>Something went wrong. Please check your backend server.</p>
        </div>

        <div class="note">
          Model can make mistakes. Also verify that the backend server is running properly.
        </div>
      `;

      resultBox.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
