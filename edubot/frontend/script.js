const chatBox = document.getElementById('chat-box');
const form = document.getElementById('chat-form');
const input = document.getElementById('user-input');

const userId = "student_001";

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const userMessage = input.value.trim();
  if (!userMessage) return;

  appendMessage('user', userMessage);
  input.value = '';

  const response = await fetch('http://127.0.0.1:8000/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ message: userMessage, user_id: userId })
  });

  const data = await response.json();
  appendMessage('bot', data.response);
});

function appendMessage(role, message) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = message;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}
