async function sendMessage() {
  const inputField = document.getElementById("user-input");
  const userText = inputField.value;
  if (!userText.trim()) return;

  const chatbox = document.getElementById("chatbox");
  chatbox.innerHTML += `<p><strong>You:</strong> ${userText}</p>`;
  inputField.value = "";

  const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userText })
  });

  const data = await response.json();
  chatbox.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
  chatbox.scrollTop = chatbox.scrollHeight;
}

function toggleMode() {
  document.body.classList.toggle("light-mode");
}

async function clearHistory() {
  const chatbox = document.getElementById("chatbox");
  await fetch("/clear", { method: "POST" });
  chatbox.innerHTML = "<p><em>Chat history cleared.</em></p>";
}
