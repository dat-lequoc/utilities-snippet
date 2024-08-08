document.addEventListener('DOMContentLoaded', function () {
    var toggleHighlighter = document.getElementById('toggleHighlighter');

    // Load the current state
    chrome.storage.sync.get('highlighterEnabled', function (data) {
        toggleHighlighter.checked = data.highlighterEnabled !== false;
    });

    // Save the state when the toggle is clicked
    toggleHighlighter.addEventListener('change', function () {
        chrome.storage.sync.set({ highlighterEnabled: this.checked });

        // Send message to content script
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            chrome.tabs.sendMessage(tabs[0].id, { action: "toggleHighlighter", enabled: toggleHighlighter.checked });
        });
    });
});