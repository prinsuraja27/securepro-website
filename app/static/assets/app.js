const tokenKey = "securepro_token";
let mode = "login";

const qs = (id) => document.getElementById(id);
const authModal = qs("authModal");
const authForm = qs("authForm");
const authNote = qs("authNote");
const authStatus = qs("authStatus");
const profileOutput = qs("profileOutput");
const nameField = qs("nameField");
const modalTitle = qs("modalTitle");
const authSubmit = qs("authSubmit");

function token() {
  return localStorage.getItem(tokenKey);
}

function setAuthStatus() {
  authStatus.textContent = token() ? "Logged in" : "Not logged in";
}

function openModal(nextMode) {
  mode = nextMode;
  authNote.textContent = "";
  authForm.reset();
  modalTitle.textContent = mode === "register" ? "Create Account" : "Login";
  authSubmit.textContent = mode === "register" ? "Create Account" : "Login";
  nameField.classList.toggle("hidden", mode !== "register");
  authModal.classList.add("show");
  authModal.setAttribute("aria-hidden", "false");
}

function closeModal() {
  authModal.classList.remove("show");
  authModal.setAttribute("aria-hidden", "true");
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token()) headers.Authorization = `Bearer ${token()}`;
  const response = await fetch(path, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

qs("menuToggle").addEventListener("click", () => qs("navLinks").classList.toggle("show"));
qs("openLogin").addEventListener("click", () => openModal("login"));
qs("openRegister").addEventListener("click", () => openModal("register"));
qs("closeModal").addEventListener("click", closeModal);
authModal.addEventListener("click", (event) => { if (event.target === authModal) closeModal(); });

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeModal();
});

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    email: qs("email").value.trim(),
    password: qs("password").value
  };
  if (mode === "register") payload.full_name = qs("fullName").value.trim();

  try {
    const path = mode === "register" ? "/api/auth/register" : "/api/auth/login";
    const result = await api(path, { method: "POST", body: JSON.stringify(payload) });
    localStorage.setItem(tokenKey, result.access_token);
    setAuthStatus();
    profileOutput.textContent = JSON.stringify(result.user, null, 2);
    authNote.textContent = "Success";
    setTimeout(closeModal, 500);
  } catch (error) {
    authNote.textContent = error.message;
  }
});

qs("loadProfile").addEventListener("click", async () => {
  try {
    const result = await api("/api/auth/me");
    profileOutput.textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    profileOutput.textContent = error.message;
  }
});

qs("loadMessages").addEventListener("click", async () => {
  try {
    const result = await api("/api/admin/messages");
    profileOutput.textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    profileOutput.textContent = error.message;
  }
});

qs("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem(tokenKey);
  setAuthStatus();
  profileOutput.textContent = "Logged out";
});

qs("contactForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const note = qs("contactNote");
  const payload = {
    name: qs("contactName").value.trim(),
    email: qs("contactEmail").value.trim(),
    message: qs("contactMessage").value.trim()
  };
  try {
    const result = await api("/api/contact", { method: "POST", body: JSON.stringify(payload) });
    note.textContent = result.message;
    event.target.reset();
  } catch (error) {
    note.textContent = error.message;
  }
});

qs("newsletterForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = qs("newsletterEmail").value.trim();
  try {
    const result = await api("/api/newsletter", { method: "POST", body: JSON.stringify({ email }) });
    alert(result.message);
    event.target.reset();
  } catch (error) {
    alert(error.message);
  }
});

setAuthStatus();
