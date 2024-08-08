let highlighterEnabled = true;

function highlightSelection() {
  if (!highlighterEnabled) return;

  let selection = window.getSelection();
  if (selection.rangeCount > 0) {
    let range = selection.getRangeAt(0);
    let selectedText = range.toString().trim();

    if (selectedText.length > 0) {
      let span = document.createElement('span');
      span.style.backgroundColor = 'yellow';
      span.textContent = `*${selectedText}*`;

      range.deleteContents();
      range.insertNode(span);

      selection.removeAllRanges();
    }
  }
}

document.addEventListener('mouseup', highlightSelection);

// Listen for messages from the popup
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action === "toggleHighlighter") {
    highlighterEnabled = request.enabled;
  }
});

// Load the initial state
chrome.storage.sync.get('highlighterEnabled', function (data) {
  highlighterEnabled = data.highlighterEnabled !== false;
});