// Example 1: Change Paragraph Text
document
  .getElementById("changeTextButton")
  .addEventListener("click", function () {
    const paragraph = document.getElementById("myParagraph");

    paragraph.textContent =
      "🎉 Awesome! The paragraph has been updated successfully.";
  });

// Example 2: Highlight First City
document
  .getElementById("highlightFirstCity")
  .addEventListener("click", function () {
    const firstCity = document.getElementById("citiesList").firstElementChild;

    firstCity.classList.toggle("highlight");
  });

// Example 3: Change Coffee Order
document.getElementById("changeOrder").addEventListener("click", function () {
  const coffeeType = document.getElementById("coffeeType");

  coffeeType.textContent = "Espresso ☕";
  coffeeType.style.background = "#8B4513";
  coffeeType.style.color = "white";
  coffeeType.style.padding = "6px 12px";
  coffeeType.style.borderRadius = "8px";
  coffeeType.style.fontWeight = "bold";
});

// Example 4: Add Shopping Item
document.getElementById("addNewItem").addEventListener("click", function () {
  const newItem = document.createElement("li");

  newItem.textContent = "🥚 Eggs";

  document.getElementById("shoppingList").appendChild(newItem);
});

// Example 5: Remove Last Task
document
  .getElementById("removeLastTask")
  .addEventListener("click", function () {
    const taskList = document.getElementById("taskList");

    if (taskList.lastElementChild) {
      taskList.lastElementChild.remove();
    }
  });

// Example 6: Double Click Event
document
  .getElementById("clickMeButton")
  .addEventListener("dblclick", function () {
    alert("☕ Welcome to ChaiCode!");
  });

// Example 7: Event Delegation
document.getElementById("teaList").addEventListener("click", function (event) {
  if (event.target.matches(".teaItem")) {
    alert(`🍵 You selected: ${event.target.textContent}`);
  }
});

// Example 8: Form Handling
document
  .getElementById("feedbackForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const feedback = document.getElementById("feedbackInput").value.trim();

    if (feedback === "") {
      alert("⚠️ Please enter your feedback.");
      return;
    }

    document.getElementById("feedbackDisplay").textContent =
      `✅ Feedback Received: ${feedback}`;

    document.getElementById("feedbackInput").value = "";
  });

// Example 9: DOM Loaded
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("domStatus").textContent =
    "✅ DOM Fully Loaded Successfully!";
});

// Example 10: Toggle Highlight
document
  .getElementById("toggleHighlight")
  .addEventListener("click", function () {
    const description = document.getElementById("descriptionText");

    description.classList.toggle("highlight");
  });
