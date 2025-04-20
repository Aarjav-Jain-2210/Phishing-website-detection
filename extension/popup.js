document.addEventListener('DOMContentLoaded', () => {
    const urlElement = document.getElementById('url');
    const statusElement = document.getElementById('status');
    const messageElement = document.getElementById('message');
    const reportButton = document.getElementById('reportButton');

    // Listen for messages from content.js
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.type === "UPDATE_POPUP") {
            urlElement.textContent = request.url;
            statusElement.textContent = request.status;
            messageElement.textContent = request.message;

            // Show report button only for suspicious URLs
            reportButton.style.display = (request.status === "Suspicious") ? "block" : "none";

            // Color-code status
            statusElement.style.color = request.status === "Legit" ? "green" :
                request.status === "Suspicious" ? "red" : "orange";
        }
    });

    // Report phishing button click
    reportButton.addEventListener('click', () => {
        alert("Reporting phishing URL: " + urlElement.textContent);
        // Add reporting logic (e.g., send to a server or Google Safe Browsing)
    });
});