from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import re
from urllib.parse import urlparse
import tldextract
from collections import Counter
from math import log2

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "*"}})

def calculate_entropy(text):
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0
    length = len(text)
    counter = Counter(text)
    entropy = -sum((count / length) * log2(count / length) for count in counter.values())
    return entropy

def is_suspicious_url(url):
    """Check if a URL is suspicious based on heuristic rules."""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()
        scheme = parsed_url.scheme.lower()
        query = parsed_url.query.lower()

        ext = tldextract.extract(url)
        domain_name = ext.domain.lower()
        full_domain = f"{ext.domain}.{ext.suffix}".lower()

        reasons = []

        # Rule 1: Suspicious keywords in domain or path
        suspicious_keywords = ['login', 'secure', 'account', 'verify', 'update', 'bank', 'password', 'signin', 'mp3', 'download', 'free', 'raid', 'torrent', 'stream']
        if any(keyword in domain or keyword in path for keyword in suspicious_keywords):
            reasons.append("suspicious or piracy-related keywords (e.g., mp3, download, raid)")

        # Rule 2: Random or gibberish domain
        consonants = 'bcdfghjklmnpqrstvwxyz'
        consonant_count = sum(1 for char in domain_name if char in consonants)
        is_gibberish = len(domain_name) > 8 and consonant_count / len(domain_name) > 0.6
        if is_gibberish:
            reasons.append("random or gibberish domain")

        # Rule 3: Suspicious TLDs
        suspicious_tlds = ['.xyz', '.info', '.online', '.club', '.site', '.top', '.work', '.pw', '.biz', '.cc', '.tk']
        if any(full_domain.endswith(tld) for tld in suspicious_tlds):
            reasons.append("suspicious TLD")

        # Rule 4: Long URL or complex path
        is_long_url = len(url) > 100
        path_depth = len(path.split('/')) - 1 if path else 0
        is_complex_path = path_depth > 2
        if is_long_url:
            reasons.append("unusually long URL")
        if is_complex_path:
            reasons.append("deep path structure")

        # Rule 5: IP address instead of domain
        is_ip_address = bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain))
        if is_ip_address:
            reasons.append("uses IP address instead of domain")

        # Rule 6: Non-HTTPS
        if scheme != 'https':
            reasons.append("lacks HTTPS")

        # Rule 7: Excessive subdomains
        subdomain_count = len(ext.subdomain.split('.')) if ext.subdomain else 0
        if subdomain_count > 2:
            reasons.append("excessive subdomains")

        # Rule 8: Special characters in domain
        special_chars = r'[-_@%+]'
        if bool(re.search(special_chars, domain_name)):
            reasons.append("special characters in domain")

        # Rule 9: High entropy in domain
        domain_entropy = calculate_entropy(domain_name)
        if domain_entropy > 3.5:
            reasons.append("high entropy (randomness) in domain")

        # Rule 10: Query parameter count
        query_param_count = len(query.split('&')) if query else 0
        if query_param_count > 3:
            reasons.append("excessive query parameters")

        # Combine rules
        is_phishing = bool(reasons)
        if is_phishing:
            message = f"Suspicious patterns detected: {', '.join(reasons)}."
        else:
            message = "This URL appears to be safe."

        return is_phishing, message
    except Exception as e:
        logging.error("Error parsing URL: %s", str(e))
        return False, "Error analyzing URL."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    logging.info("Received request: %s", request.get_json())
    url = request.get_json().get('url', '')
    if not url:
        return jsonify({"phishing": False, "message": "No URL provided."})

    is_phishing, message = is_suspicious_url(url)
    logging.info("Prediction for %s: %s", url, is_phishing)
    return jsonify({"phishing": is_phishing, "message": message})

if __name__ == '__main__':
    logging.info("Starting Flask server...")
    try:
        app.run(debug=True, host='0.0.0.0', port=8080)
    except Exception as e:
        logging.error("Failed to start server: %s", str(e))
        raise