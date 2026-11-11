/**
 * CareerAI Advisor Chatbot Widget.
 * Injects floating chat widget and handles interactive conversation with the Flask AI backend.
 */

(function initChatbot() {
  document.addEventListener('DOMContentLoaded', () => {
    // Only inject if not already present
    if (document.getElementById('chatbot-widget-container')) return;

    const container = document.createElement('div');
    container.id = 'chatbot-widget-container';
    container.innerHTML = `
      <!-- Launcher Button -->
      <button class="chatbot-launcher" id="chatbot-launcher" title="Chat with CareerAI Advisor" aria-label="Open Career Guidance Chatbot">
        <div class="launcher-icon">
          <i class="fas fa-robot"></i>
        </div>
        <span>CareerAI Advisor</span>
      </button>

      <!-- Chatbot Dialog Window -->
      <div class="chatbot-window" id="chatbot-window">
        <div class="chatbot-header">
          <div class="chatbot-header-info">
            <div class="chatbot-avatar">
              <i class="fas fa-brain"></i>
            </div>
            <div>
              <h4 class="chatbot-title">CareerAI Advisor</h4>
              <span class="chatbot-subtitle"><i class="fas fa-circle" style="color: #4ade80; font-size: 0.55rem;"></i> Intelligent Career Counselor</span>
            </div>
          </div>
          <button class="chatbot-close-btn" id="chatbot-close-btn" title="Close Chat" aria-label="Close Chat">&times;</button>
        </div>

        <div class="chatbot-body" id="chatbot-messages">
          <!-- Initial Welcome Message -->
          <div class="chat-bubble bot">
            <p><strong>Hi there! 👋 I am your CareerAI Advisor.</strong></p>
            <p>Ask me anything about technology careers, required skills, missing competencies, or project ideas!</p>
            <div class="chat-suggestions">
              <button class="suggestion-chip" onclick="window.sendChatSuggestion('What are my Top 3 career matches?')">🎯 What are my Top 3 career matches?</button>
              <button class="suggestion-chip" onclick="window.sendChatSuggestion('What skills should I learn next?')">🚀 What skills should I learn next?</button>
              <button class="suggestion-chip" onclick="window.sendChatSuggestion('Compare Data Analyst vs Data Scientist')">⚖️ Compare Data Analyst vs Data Scientist</button>
              <button class="suggestion-chip" onclick="window.sendChatSuggestion('Suggest portfolio projects for me')">💡 Suggest portfolio projects</button>
            </div>
          </div>

          <div class="chat-typing-indicator" id="chat-typing">
            <i class="fas fa-circle-notch fa-spin"></i> CareerAI is thinking...
          </div>
        </div>

        <div class="chatbot-footer">
          <input type="text" class="chatbot-input" id="chatbot-input" placeholder="Ask about tech careers, skills, projects..." />
          <button class="chatbot-send-btn" id="chatbot-send-btn" title="Send Message" aria-label="Send Message">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(container);

    // Event listeners
    const launcher = document.getElementById('chatbot-launcher');
    const win = document.getElementById('chatbot-window');
    const closeBtn = document.getElementById('chatbot-close-btn');
    const sendBtn = document.getElementById('chatbot-send-btn');
    const input = document.getElementById('chatbot-input');

    launcher.addEventListener('click', () => {
      win.classList.toggle('active');
      if (win.classList.contains('active')) {
        input.focus();
      }
    });

    closeBtn.addEventListener('click', () => {
      win.classList.remove('active');
    });

    sendBtn.addEventListener('click', () => handleUserSend());

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleUserSend();
      }
    });
  });

  window.sendChatSuggestion = function(text) {
    const input = document.getElementById('chatbot-input');
    if (input) {
      input.value = text;
      handleUserSend();
    }
  };

  async function handleUserSend() {
    const input = document.getElementById('chatbot-input');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    appendMessage(msg, 'user');

    const typing = document.getElementById('chat-typing');
    const msgContainer = document.getElementById('chatbot-messages');
    if (typing) {
      typing.classList.add('active');
      msgContainer.scrollTop = msgContainer.scrollHeight;
    }

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });

      const data = await res.json();
      if (typing) typing.classList.remove('active');

      if (data.status === 'success') {
        appendBotMessage(data.reply, data.suggestions || []);
      } else {
        appendBotMessage(data.message || 'Sorry, I encountered an issue. Please try again.', []);
      }
    } catch (err) {
      if (typing) typing.classList.remove('active');
      appendBotMessage('Network error communicating with CareerAI advisor.', []);
    }
  }

  function appendMessage(text, sender) {
    const msgContainer = document.getElementById('chatbot-messages');
    const typing = document.getElementById('chat-typing');

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.textContent = text;

    if (typing && msgContainer.contains(typing)) {
      msgContainer.insertBefore(bubble, typing);
    } else {
      msgContainer.appendChild(bubble);
    }

    msgContainer.scrollTop = msgContainer.scrollHeight;
  }

  function appendBotMessage(replyMarkdown, suggestions) {
    const msgContainer = document.getElementById('chatbot-messages');
    const typing = document.getElementById('chat-typing');

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble bot';

    // Simple markdown formatting for bold, bullets, newlines
    let html = replyMarkdown
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n- (.*?)(?=(\n|$))/g, '<br>&bull; $1')
      .replace(/\n/g, '<br>');

    html = `<p>${html}</p>`;

    if (suggestions && suggestions.length > 0) {
      html += `
        <div class="chat-suggestions">
          ${suggestions.map(s => `
            <button class="suggestion-chip" onclick="window.sendChatSuggestion('${s.replace(/'/g, "\\'")}')">${s}</button>
          `).join('')}
        </div>
      `;
    }

    bubble.innerHTML = html;

    if (typing && msgContainer.contains(typing)) {
      msgContainer.insertBefore(bubble, typing);
    } else {
      msgContainer.appendChild(bubble);
    }

    msgContainer.scrollTop = msgContainer.scrollHeight;
  }

})();
