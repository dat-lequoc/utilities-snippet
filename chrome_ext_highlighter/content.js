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
}

document.addEventListener('mouseup', highlightSelection);

// Listen for messages from the popup
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action === "toggleHighlighter") {
    highlighterEnabled = request.enabled;
  } else if (request.action === "copyAllText") {
    copyAllText();
  }
});

// Load the initial state
chrome.storage.sync.get('highlighterEnabled', function (data) {
  highlighterEnabled = data.highlighterEnabled === true;
});