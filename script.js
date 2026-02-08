const chatContainer = document.getElementById("chatContainer");
const chatForm = document.getElementById("chatForm");
const promptInput = document.getElementById("promptInput");
const headerSection = document.getElementById("headerSection");

// Message HTML Banane ka Function
const createMessageHTML = (text, isUser, isLoading = false) => {
  const className = isUser ? "message--outgoing" : "message--incoming";
  const icon = isUser ? "bx-user" : "bx-bot";
  
  // Agar loading hai to text badal do
  const content = isLoading 
    ? `<div class="loading-animation">Thinking...</div>` 
    : marked.parse(text); // Markdown formatting

  return `
    <div class="message ${className}">
      <div class="message__content">
        <div class="message__icon"><i class='bx ${icon}'></i></div>
        <div class="message__text">${content}</div>
      </div>
    </div>
  `;
};

// API Call Function
const generateResponse = async (userText) => {
  // 1. Loading Message Dikhao
  const loadingDiv = document.createElement("div");
  loadingDiv.innerHTML = createMessageHTML("", false, true);
  chatContainer.appendChild(loadingDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  try {
    // 2. Vercel Python API ko call karo
    const response = await fetch('/api', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
          question: userText,
          source: 'web_ui'
      })
    });

    const data = await response.json();
    
    // 3. Loading hatao aur asli jawab dikhao
    chatContainer.removeChild(loadingDiv);
    
    const botDiv = document.createElement("div");
    botDiv.innerHTML = createMessageHTML(data.answer, false);
    chatContainer.appendChild(botDiv);

  } catch (error) {
    chatContainer.removeChild(loadingDiv);
    const errorDiv = document.createElement("div");
    errorDiv.innerHTML = createMessageHTML("Error: Server connect nahi hua.", false);
    chatContainer.appendChild(errorDiv);
  }
  
  chatContainer.scrollTop = chatContainer.scrollHeight;
};

// Form Submit Handler
const handleOutgoingChat = (e) => {
  e.preventDefault();
  const userText = promptInput.value.trim();
  if (!userText) return;

  // Header ko chhupao
  headerSection.style.display = "none";

  // User ka message add karo
  const userDiv = document.createElement("div");
  userDiv.innerHTML = createMessageHTML(userText, true);
  chatContainer.appendChild(userDiv);

  promptInput.value = "";
  chatContainer.scrollTop = chatContainer.scrollHeight;

  // Bot se jawaab mango
  generateResponse(userText);
};

// Helper function for suggestions
window.fillPrompt = (text) => {
    promptInput.value = text;
    chatForm.dispatchEvent(new Event('submit'));
}

chatForm.addEventListener("submit", handleOutgoingChat);
