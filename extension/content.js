console.log("Content script running on: " + window.location.href);

// Function to check URL with Flask server
function checkURL(url) {
    console.log("Checking URL: " + url);
    fetch('http://localhost:5050/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("Server response: ", data);
            let status = data.phishing ? "Suspicious" : "Legit";
            let message = data.message || (data.phishing ? "Warning: This URL is likely a phishing site!" : "This URL appears to be safe.");

            // Show alert
            alert(message);

            // Show notification
            chrome.runtime.sendMessage({
                type: "SHOW_NOTIFICATION",
                message: `URL Status: ${status}\n${message}`,
                phishing: data.phishing
            });

            // Update popup with result
            chrome.runtime.sendMessage({
                type: "UPDATE_POPUP",
                status: status,
                message: message,
                url: url
            });
        })
        .catch(error => {
            console.error("Error checking URL: ", error);
            let errorMessage = "Error: Could not verify URL. Server may be down.";
            alert(errorMessage);
            chrome.runtime.sendMessage({
                type: "SHOW_NOTIFICATION",
                message: errorMessage,
                phishing: false
            });
            chrome.runtime.sendMessage({
                type: "UPDATE_POPUP",
                status: "Error",
                message: errorMessage,
                url: url
            });
        });
}

// Check the current page's URL
checkURL(window.location.href);