const chatContainer = document.getElementById("chatContainer");
const chatForm = document.getElementById("chatForm");
const promptInput = document.getElementById("promptInput");
const headerSection = document.getElementById("headerSection");

// Message HTML Structure
const createMessageElement = (content, className) => {
  const div = document.createElement("div");
  div.classList.add("message", className);
  div.innerHTML = content;
  return div;
}

// Backend API Call
const getBotResponse = async (userText, loadingDiv) => {
  try {
    const response = await fetch('/api', {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
          question: userText,
          source: 'web_ui' 
      })
    });

    const data = await response.json();
    
    // Loading hatao aur asli jawab dikhao
    chatContainer.removeChild(loadingDiv);
    
    // Markdown ko HTML mein badlo (Bold, Code, etc.)
    const botHtml = `<div class="message__content">
                        <img class="message__avatar" src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png" alt="AI">
                        <div class="message__text">${marked.parse(data.answer)}</div>
                     </div>`;
                     
    const botDiv = createMessageElement(botHtml, "message--incoming");
    chatContainer.appendChild(botDiv);
    
    // Code Blocks ko highlight karo
    document.querySelectorAll('pre code').forEach((el) => {
        hljs.highlightElement(el);
    });
    
    chatContainer.scrollTop = chatContainer.scrollHeight;

  } catch (error) {
    chatContainer.removeChild(loadingDiv);
    const errorHtml = `<div class="message__content"><div class="message__text" style="color:red;">Error: Server connect nahi hua.</div></div>`;
    chatContainer.appendChild(createMessageElement(errorHtml, "message--error"));
  }
}

// Form Submit Handler
const handleOutgoingChat = (e) => {
  e.preventDefault();
  const userText = promptInput.value.trim();
  if (!userText) return;

  // Header chupao jab chat shuru ho
  headerSection.style.display = "none";

  // User Message Add karo
  const userHtml = `<div class="message__content">
                      <div class="message__text">${userText}</div>
                      <img class="message__avatar" src="https://cdn-icons-png.flaticon.com/512/1144/1144760.png" alt="User">
                    </div>`;
  const userDiv = createMessageElement(userHtml, "message--outgoing");
  chatContainer.appendChild(userDiv);
  
  promptInput.value = "";
  chatContainer.scrollTop = chatContainer.scrollHeight;

  // Loading Animation Add karo
  const loadingHtml = `<div class="message__content">
                         <img class="message__avatar" src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png" alt="AI">
                         <div class="message__text">Thinking...</div>
                       </div>`;
  const loadingDiv = createMessageElement(loadingHtml, "message--incoming");
  chatContainer.appendChild(loadingDiv);

  getBotResponse(userText, loadingDiv);
}

// Suggestion Click Helper
window.fillPrompt = (text) => {
    promptInput.value = text;
    chatForm.dispatchEvent(new Event('submit'));
}

chatForm.addEventListener("submit", handleOutgoingChat);

