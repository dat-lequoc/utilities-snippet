chrome.commands.onCommand.addListener((command) => {
    if (command === "toggle-highlighter") {
        chrome.storage.sync.get('highlighterEnabled', (data) => {
            const newState = !data.highlighterEnabled;
            chrome.storage.sync.set({ highlighterEnabled: newState });
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                chrome.tabs.sendMessage(tabs[0].id, { action: "toggleHighlighter", enabled: newState });
            });
        });
    }
});