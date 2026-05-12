// Chat Widget Functionality
// Provides AI chat feature accessible from all pages

let chatWidgetMinimized = false;
let initialMessageSent = false;

function initChatWidget() {
  // Widget is initialized but remains hidden until Ask AI button is clicked
  // Initial message will be sent when widget is first opened
}

function openChatWidget() {
  const widget = document.getElementById('chat-widget');
  if (widget) {
    widget.classList.remove('minimized');
    widget.classList.add('active');
    chatWidgetMinimized = false;
    
    // Send initial message on first open
    if (!initialMessageSent) {
      initialMessageSent = true;
      sendInitialMessage();
    }
    
    const input = document.getElementById('chat-input');
    if (input) {
      input.focus();
    }
  }
}

function closeChatWidget() {
  const widget = document.getElementById('chat-widget');
  if (widget) {
    widget.classList.remove('active');
    widget.classList.add('minimized');
  }
}

function minimizeChatWidget() {
  const widget = document.getElementById('chat-widget');
  if (widget) {
    widget.classList.toggle('minimized');
    chatWidgetMinimized = !chatWidgetMinimized;
  }
}

async function sendInitialMessage() {
  const messagesContainer = document.getElementById('chat-messages');
  if (!messagesContainer) return;
  
  // Clear any existing messages
  messagesContainer.innerHTML = '';
  
  // Add AI's first message
  addChatMessage('ai', 'How can I help you?');
}

async function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const messagesContainer = document.getElementById('chat-messages');
  const sendBtn = document.getElementById('chat-send-btn');
  
  if (!input || !messagesContainer) return;
  
  const message = input.value.trim();
  if (!message) return;
  
  // Disable button during sending
  if (sendBtn) {
    sendBtn.disabled = true;
    sendBtn.textContent = '...';
  }
  
  // Add user message
  addChatMessage('user', message);
  input.value = '';
  
  // Show typing indicator
  const typingId = addChatMessage('ai', 'Thinking...');
  
  try {
    const res = await apiFetch('/ai/chat', 'POST', { message: message });
    
    // Remove typing indicator
    const typingEl = document.getElementById(typingId);
    if (typingEl) typingEl.remove();
    
    if (res.success) {
      addChatMessage('ai', res.data.answer || 'I\'m ready to help. What would you like to know?');
    } else {
      addChatMessage('ai', res.message || 'Sorry, I encountered an error. Please try again.');
    }
  } catch (error) {
    const typingEl = document.getElementById(typingId);
    if (typingEl) typingEl.remove();
    addChatMessage('ai', 'Network error. Please check your connection.');
  }
  
  // Re-enable button
  if (sendBtn) {
    sendBtn.disabled = false;
    sendBtn.textContent = 'Send';
  }
  
  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addChatMessage(sender, text) {
  const messagesContainer = document.getElementById('chat-messages');
  if (!messagesContainer) return null;
  
  const messageId = 'msg-' + Date.now();
  const div = document.createElement('div');
  div.id = messageId;
  div.className = 'chat-message chat-message-' + sender;
  
  const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  
  div.innerHTML = '<div class="chat-message-content">' + escapeHtml(text) + '</div>' +
    '<div class="chat-message-time">' + timestamp + '</div>';
  
  messagesContainer.appendChild(div);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  
  return messageId;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Handle Enter key in chat input
document.addEventListener('DOMContentLoaded', function() {
  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
      }
    });
  }
  
  // Initialize chat widget after DOM is ready
  initChatWidget();
});
