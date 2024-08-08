let highlighterEnabled = false;

function highlightSelection() {
  if (!highlighterEnabled) return;

  let selection = window.getSelection();
  if (selection.rangeCount > 0) {
    let range = selection.getRangeAt(0);
    let selectedText = range.toString().trim();

    if (selectedText.length > 0) {
      let span = document.createElement('span');
      span.style.backgroundColor = 'yellow';
      span.textContent = `**${selectedText}** `;

      range.deleteContents();
      range.insertNode(span);

      selection.removeAllRanges();
    }
  }
}

function extractMainContent() {
  // Common selectors for main content
  const contentSelectors = [
    'article',
    '[role="main"]',
    '.main-content',
    '#main-content',
    '.post-content',
    '.entry-content',
    '.article-content',
    '.content-area'
  ];

  for (let selector of contentSelectors) {
    const element = document.querySelector(selector);
    if (element) {
      return element.innerText;
    }
  }

  // If no matching element found, fall back to body text
  return document.body.innerText;
}

function copyAllText() {
  const mainContent = extractMainContent();
  const el = document.createElement('textarea');
  el.value = mainContent;
  el.setAttribute('readonly', '');
  el.style.position = 'absolute';
  el.style.left = '-9999px';
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);
  return true;
}

function copyWithInstructions() {
  fetch(chrome.runtime.getURL('instructions_claude.txt'))
    .then(response => response.text())
    .then(instructions => {
      const mainContent = extractMainContent();
      const textToCopy = `${instructions}\n\n${mainContent}`;
      const el = document.createElement('textarea');
      el.value = textToCopy;
      el.setAttribute('readonly', '');
      el.style.position = 'absolute';
      el.style.left = '-9999px';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      return true;
    })
    .catch(error => {
      console.error('Error reading instructions file:', error);
      return false;
    });
}

function showNotification(message) {
  const notification = document.createElement('div');
  notification.textContent = message;
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #4CAF50;
        color: white;
        padding: 15px;
        border-radius: 5px;
        z-index: 9999;
    `;
  document.body.appendChild(notification);
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

document.addEventListener('mouseup', highlightSelection);

// Listen for messages from the popup
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action === "toggleHighlighter") {
    highlighterEnabled = request.enabled;
  } else if (request.action === "copyAllText") {
    const success = copyAllText();
    sendResponse({ success: success });
  } else if (request.action === "copyWithInstructions") {
    copyWithInstructions().then(success => {
      sendResponse({ success: success });
    });
    return true; // Indicates that the response is asynchronous
  } else if (request.action === "showNotification") {
    showNotification(request.message);
  }
  return true;
});

// Load the initial state
chrome.storage.sync.get('highlighterEnabled', function (data) {
  highlighterEnabled = data.highlighterEnabled === true;
});