// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "sendUrl" || message.action === "urlChanged") {
        const urlToCheck = message.url;
        console.log('URL received from content script:', urlToCheck);

        // Call the prediction API
        fetch('http://127.0.0.1:5050/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: urlToCheck })
        })
            .then(response => response.json())
            .then(data => {
                console.log('API Response:', data);

                if (data.error) {
                    console.error('API Error:', data.error);
                    return;
                }

                const isPhishing = data.phishing;
                const message = data.message || (isPhishing ? `The site ${urlToCheck} is suspected of phishing!` : `The site ${urlToCheck} is safe.`);

                // Send result to content script and popup
                chrome.runtime.sendMessage({
                    action: "predictionResult",
                    result: isPhishing ? "phishing" : "safe",
                    message: message
                });

                // Show notification for phishing sites
                if (isPhishing) {
                    chrome.notifications.create({
                        type: 'basic',
                        iconUrl: 'alert.png',
                        title: '⚠️ Phishing Alert!',
                        message: message,
                        priority: 2
                    });
                }
            })
            .catch(error => {
                console.error('❌ Error fetching prediction:', error.message || error);
            });
    }
});
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "SHOW_NOTIFICATION") {
        chrome.notifications.create({
            type: "basic",
            iconUrl: "alert.png",
            title: "Phishing Detector",
            message: request.message,
            priority: 2
        });
    }
});
// Listen for tab updates (new page loads)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        console.log(`Tab updated: ${tabId}, URL: ${tab.url}`);

        // Call the prediction API
        fetch('http://127.0.0.1:5050/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: tab.url })
        })
            .then(response => response.json())
            .then(data => {
                console.log('API Response from tab update:', data);

                if (data.error) {
                    console.error('API Error:', data.error);
                    return;
                }

                const isPhishing = data.phishing;
                const message = data.message || (isPhishing ? `The site ${tab.url} is suspected of phishing!` : `The site ${tab.url} is safe.`);

                // Send result to content script and popup
                chrome.runtime.sendMessage({
                    action: "predictionResult",
                    result: isPhishing ? "phishing" : "safe",
                    message: message
                });

                // Show notification for phishing sites
                if (isPhishing) {
                    chrome.notifications.create({
                        type: 'basic',
                        iconUrl: 'alert.png',
                        title: '⚠️ Phishing Alert!',
                        message: message,
                        priority: 2
                    });
                } else {
                    console.log('✅ Safe site:', tab.url);
                }
            })
            .catch(error => {
                console.error('❌ Error during tab update fetch:', error.message || error);
            });
    }
});