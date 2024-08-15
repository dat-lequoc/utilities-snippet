document.addEventListener('DOMContentLoaded', function () {
    var toggleHighlighter = document.getElementById('toggleHighlighter');
    var copyButton = document.getElementById('copyButton');
    var copyWithInstructionsButton = document.getElementById('copyWithInstructionsButton');
    var openClaudeButton = document.getElementById('openClaudeButton');

    // Load the current state
    chrome.storage.sync.get('highlighterEnabled', function (data) {
        toggleHighlighter.checked = data.highlighterEnabled === true;
    });

    // Save the state when the toggle is clicked
    toggleHighlighter.addEventListener('change', function () {
        chrome.storage.sync.set({ highlighterEnabled: this.checked });

        // Send message to content script
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            chrome.tabs.sendMessage(tabs[0].id, { action: "toggleHighlighter", enabled: toggleHighlighter.checked });
        });
    });

    // Handle copy button click
    copyButton.addEventListener('click', function () {
        performCopyAction("copyAllText", "Text copied successfully!");
    });

    // Handle copy with instructions button click
    copyWithInstructionsButton.addEventListener('click', function () {
        performCopyAction("copyWithInstructions", "Text copied with instructions successfully!");
    });

    // Handle open in Claude AI button click
    openClaudeButton.addEventListener('click', function () {
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            chrome.tabs.sendMessage(tabs[0].id, { action: "getTextWithInstructions" }, function (response) {
                if (response && response.text) {
                    const encodedText = encodeURIComponent(response.text);
                    const claudeUrl = `https://claude.ai/new?q=${encodedText}`;
                    chrome.tabs.create({ url: claudeUrl });
                    window.close();
                } else {
                    chrome.tabs.sendMessage(tabs[0].id, { action: "showNotification", message: "Error: Failed to get text" });
                }
            });
        });
    });

    function performCopyAction(action, successMessage) {
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            chrome.tabs.sendMessage(tabs[0].id, { action: action }, function (response) {
                if (response && response.success) {
                    // Close the popup
                    window.close();

                    // Show a notification
                    chrome.tabs.sendMessage(tabs[0].id, { action: "showNotification", message: successMessage });
                } else {
                    // Show an error notification
                    chrome.tabs.sendMessage(tabs[0].id, { action: "showNotification", message: "Error: Copy action failed" });
                }
            });
        });
    }
});