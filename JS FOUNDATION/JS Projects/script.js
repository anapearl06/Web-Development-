// Select Elements
const taskInput = document.getElementById("taskInput");
const addTaskBtn = document.getElementById("addTaskBtn");
const taskList = document.getElementById("taskList");

const taskCount = document.getElementById("taskCount");
const completedCount = document.getElementById("completedCount");
const pendingCount = document.getElementById("pendingCount");

const filterBtns = document.querySelectorAll(".filter-btn");

const clearCompleted = document.getElementById("clearCompleted");
const deleteAll = document.getElementById("deleteAll");

const emptyState = document.getElementById("emptyState");

// Store Tasks
let tasks = JSON.parse(localStorage.getItem("tasks")) || [];

let currentFilter = "all";

// Add Task
addTaskBtn.addEventListener("click", addTask);

taskInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    addTask();
  }
});

function addTask() {
  const text = taskInput.value.trim();

  if (text === "") {
    alert("Please enter a task!");
    return;
  }

  const task = {
    id: Date.now(),

    text: text,

    completed: false,
  };

  tasks.push(task);

  saveTasks();

  taskInput.value = "";

  renderTasks();
}

// Display Tasks
function renderTasks() {
  taskList.innerHTML = "";

  let filteredTasks = tasks;

  if (currentFilter === "completed") {
    filteredTasks = tasks.filter((task) => task.completed);
  }

  if (currentFilter === "pending") {
    filteredTasks = tasks.filter((task) => !task.completed);
  }

  filteredTasks.forEach((task) => {
    const li = document.createElement("li");

    li.className = "task";

    if (task.completed) {
      li.classList.add("completed");
    }

    li.innerHTML = `

            <span>${task.text}</span>

            <div class="actions">

                <button class="complete-btn">
                    ✔️
                </button>

                <button class="edit-btn">
                    ✏️
                </button>

                <button class="delete-btn">
                    🗑️
                </button>

            </div>

        `;

    // Complete
    li.querySelector(".complete-btn").addEventListener("click", () => {
      task.completed = !task.completed;

      saveTasks();

      renderTasks();
    });

    // Edit
    li.querySelector(".edit-btn").addEventListener("click", () => {
      const updatedTask = prompt("Edit your task:", task.text);

      if (updatedTask) {
        task.text = updatedTask;

        saveTasks();

        renderTasks();
      }
    });

    // Delete
    li.querySelector(".delete-btn").addEventListener("click", () => {
      tasks = tasks.filter((item) => item.id !== task.id);

      saveTasks();

      renderTasks();
    });

    taskList.appendChild(li);
  });

  updateStats();
}

// Update Counters
function updateStats() {
  const completed = tasks.filter((task) => task.completed).length;

  const pending = tasks.length - completed;

  taskCount.textContent = tasks.length;

  completedCount.textContent = completed;

  pendingCount.textContent = pending;

  if (tasks.length === 0) {
    emptyState.style.display = "block";
  } else {
    emptyState.style.display = "none";
  }
}

// Filters
filterBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    filterBtns.forEach((button) => {
      button.classList.remove("active");
    });

    btn.classList.add("active");

    currentFilter = btn.dataset.filter;

    renderTasks();
  });
});

// Clear Completed
clearCompleted.addEventListener("click", () => {
  tasks = tasks.filter((task) => !task.completed);

  saveTasks();

  renderTasks();
});

// Delete All
deleteAll.addEventListener("click", () => {
  if (confirm("Delete all tasks?")) {
    tasks = [];

    saveTasks();

    renderTasks();
  }
});

// Save Tasks
function saveTasks() {
  localStorage.setItem("tasks", JSON.stringify(tasks));
}

// Initial Load
renderTasks();
