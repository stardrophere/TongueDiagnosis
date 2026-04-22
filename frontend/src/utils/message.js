let messageContainer = null;

function createContainer() {
  if (messageContainer) return;
  messageContainer = document.createElement('div');
  messageContainer.className = 'custom-message-container';
  document.body.appendChild(messageContainer);

  const style = document.createElement('style');
  style.textContent = `
    .custom-message-container {
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    }
    .custom-message {
      padding: 12px 20px;
      border-radius: 8px;
      background: white;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      font-size: 14px;
      color: #333;
      display: flex;
      align-items: center;
      gap: 8px;
      animation: message-slide-in 0.3s ease-out;
      pointer-events: auto;
    }
    .custom-message.success { border-left: 4px solid #10b981; }
    .custom-message.error { border-left: 4px solid #ef4444; }
    .custom-message.warning { border-left: 4px solid #f59e0b; }
    .custom-message.info { border-left: 4px solid #3b82f6; }
    @keyframes message-slide-in {
      from { transform: translateY(-20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
}

function showMessage(text, type = 'info', duration = 3000) {
  createContainer();
  const el = document.createElement('div');
  el.className = `custom-message ${type}`;
  el.textContent = text;
  
  messageContainer.appendChild(el);
  
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(-20px)';
    el.style.transition = 'all 0.3s';
    setTimeout(() => el.remove(), 300);
  }, duration);
}

export const Message = {
  success: (text) => showMessage(text, 'success'),
  error: (text) => showMessage(text, 'error'),
  warning: (text) => showMessage(text, 'warning'),
  info: (text) => showMessage(text, 'info'),
};