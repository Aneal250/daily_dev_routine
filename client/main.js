// --- CONFIG & GLOBAL STATE ---
const API_URL = "http://127.0.0.1:5000"; // Your Flask backend URL
const defaultHabits = [
  {
    habit: "Check Company Updates",
    description: "Check Missed Updates on Slack and Emails,",
  },
  {
    habit: "Check PRs",
    description:
      "Check Personal Open PRs and Check Conflicts if everything is fine,",
  },
  {
    habit: "Know Your Products",
    description:
      "Spend time understanding the products you work with, their features, and their benefits.",
  },
  {
    habit: "Find What You Can Do",
    description:
      "Read the documentation and explore the codebase to find ways to contribute.",
  },
  {
    habit: "Improvements",
    description:
      "Identify areas for improvement in the codebase or processes and suggest changes.",
  },
  {
    habit: "Emails",
    description:
      "Check and respond to emails, especially those related to work or projects.",
  },
  {
    habit: "Read Tech Blogs",
    description:
      "Stay updated with the latest trends and technologies in your field by reading tech blogs.",
  },
  {
    habit: "Learn New Skills",
    description:
      "Dedicate time to learning new programming languages, frameworks, or tools.",
  },
  {
    habit: "Network with Peers",
    description:
      "Engage with colleagues and peers in discussions about projects, challenges, and solutions.",
  },
  {
    habit: "Reflect on Daily Progress",
    description:
      "At the end of the day, reflect on what you accomplished and plan for tomorrow.",
  },
];

// --- DOM ELEMENTS ---
const authContainer = document.getElementById("authContainer");
const appContainer = document.getElementById("appContainer");
const loginView = document.getElementById("loginView");
const registerView = document.getElementById("registerView");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const showRegister = document.getElementById("showRegister");
const showLogin = document.getElementById("showLogin");
const logoutBtn = document.getElementById("logoutBtn");
const datePicker = document.getElementById("datePicker");
const habitList = document.getElementById("habitList");
const messageArea = document.getElementById("messageArea");

// --- HELPER FUNCTIONS ---
const getToken = () => localStorage.getItem("jwt_token");
const setToken = (token) => localStorage.setItem("jwt_token", token);
const clearToken = () => localStorage.removeItem("jwt_token");

function showMessage(msg, isError = true) {
  messageArea.textContent = msg;
  messageArea.style.color = isError ? "#e74c3c" : "#27ae60";
}

// --- API CALLS ---
async function fetchTodos(date) {
  const token = getToken();
  if (!token) return logout();

  try {
    const response = await fetch(`${API_URL}/todos?date=${date}`, {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 401) return logout();
    if (!response.ok) throw new Error("Failed to fetch todos.");

    const data = await response.json();

    if (data.todos.length === 0) {
      // If no todos for this day, create them from the default list
      await createInitialTodosForDate(date);
    } else {
      renderTodos(data.todos, date);
    }
  } catch (error) {
    showMessage(error.message);
  }
}

async function createInitialTodosForDate(date) {
  const token = getToken();
  const newTodos = defaultHabits.map((h) => ({
    id: crypto.randomUUID(), // Generate UUID on the client
    todo: h.habit,
    description: h.description,
    isChecked: false,
  }));

  try {
    const response = await fetch(`${API_URL}/todos`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ date, todos: newTodos }),
    });

    if (!response.ok)
      throw new Error("Failed to initialize todos for the day.");

    renderTodos(newTodos, date); // Render the newly created todos
  } catch (error) {
    showMessage(error.message);
  }
}

async function updateTodoStatus(todoId, isChecked, date) {
  const token = getToken();
  try {
    const response = await fetch(`${API_URL}/todos/mark`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        date: date,
        todoId: todoId,
        isChecked: isChecked,
      }),
    });

    if (!response.ok) throw new Error("Failed to update todo status.");

    // Re-fetch to ensure UI is in sync with the database
    fetchTodos(date);
  } catch (error) {
    showMessage(error.message);
  }
}

// --- UI RENDERING & LOGIC ---
function renderTodos(todos, date) {
  habitList.innerHTML = "";
  todos.forEach((todo) => {
    const habitDiv = document.createElement("div");
    habitDiv.className = `habit ${todo.isChecked ? "completed" : ""}`;

    const infoDiv = document.createElement("div");
    infoDiv.className = "habit-info";
    infoDiv.innerHTML = `<h3>${todo.todo}</h3><p>${todo.description}</p>`;

    const btn = document.createElement("button");
    btn.textContent = todo.isChecked ? "Completed" : "Mark Done";
    btn.className = `mark-btn ${todo.isChecked ? "completed" : ""}`;
    btn.onclick = () => updateTodoStatus(todo.id, !todo.isChecked, date);

    habitDiv.appendChild(infoDiv);
    habitDiv.appendChild(btn);
    habitList.appendChild(habitDiv);
  });
}

function setupApp() {
  authContainer.classList.add("hidden");
  appContainer.classList.remove("hidden");
  showMessage(""); // Clear any old messages

  // Set date picker to today and fetch data
  const todayStr = new Date().toISOString().split("T")[0];
  datePicker.value = todayStr;
  fetchTodos(todayStr);
}

function logout() {
  clearToken();
  authContainer.classList.remove("hidden");
  appContainer.classList.add("hidden");
  loginForm.reset();
  registerForm.reset();
}

// --- EVENT LISTENERS ---
showRegister.addEventListener("click", () => {
  loginView.classList.add("hidden");
  registerView.classList.remove("hidden");
  showMessage("");
});

showLogin.addEventListener("click", () => {
  registerView.classList.add("hidden");
  loginView.classList.remove("hidden");
  showMessage("");
});

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  showMessage("");
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  try {
    const response = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || "Login failed");

    setToken(data.token);
    setupApp();
  } catch (error) {
    showMessage(error.message);
  }
});

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  showMessage("");
  const firstName = document.getElementById("registerFirstName").value;
  const lastName = document.getElementById("registerLastName").value;
  const email = document.getElementById("registerEmail").value;
  const password = document.getElementById("registerPassword").value;

  try {
    const response = await fetch(`${API_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, firstName, lastName }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.message || "Registration failed.");

    showMessage("Registration successful! Please login.", false);
    showLogin.click(); // Switch to login view
  } catch (error) {
    showMessage(error.message);
  }
});

logoutBtn.addEventListener("click", logout);

datePicker.addEventListener("change", (e) => fetchTodos(e.target.value));

// --- INITIALIZATION ---
function checkInitialState() {
  if (getToken()) {
    setupApp();
  } else {
    logout(); // Ensures the auth view is shown
  }
}

checkInitialState();
