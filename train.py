import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
from urllib.parse import urlparse

# Function to extract features (same as in app.py)
def extract_features(url):
    features = {}
    parsed_url = urlparse(url)
    
    def count_occurrences(char):
        return url.count(char)
    
    features['length_url'] = len(url)
    features['length_hostname'] = len(parsed_url.netloc)
    features['nb_dots'] = count_occurrences('.')
    features['nb_hyphens'] = count_occurrences('-')
    features['nb_at'] = count_occurrences('@')
    features['nb_qm'] = count_occurrences('?')
    features['nb_and'] = count_occurrences('&')
    features['nb_eq'] = count_occurrences('=')
    features['nb_underscore'] = count_occurrences('_')
    features['nb_tilde'] = count_occurrences('~')
    features['nb_percent'] = count_occurrences('%')
    features['nb_slash'] = count_occurrences('/')
    features['nb_colon'] = count_occurrences(':')
    features['nb_comma'] = count_occurrences(',')
    features['nb_semicolumn'] = count_occurrences(';')
    features['nb_dollar'] = count_occurrences('$')
    features['nb_space'] = count_occurrences(' ')
    features['nb_www'] = url.count('www')
    features['nb_com'] = url.count('.com')
    features['nb_dslash'] = url.count('//')
    features['ratio_digits_url'] = sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0
    features['ratio_digits_host'] = sum(c.isdigit() for c in parsed_url.netloc) / len(parsed_url.netloc) if len(parsed_url.netloc) > 0 else 0
    
    return list(features.values())

# Load dataset
dataset_path = 'data.csv'  # In Model directory
try:
    df = pd.read_csv(dataset_path)
    print("Columns in data.csv:", df.columns.tolist())
except FileNotFoundError:
    print(f"Error: {dataset_path} not found")
    exit(1)

# Check if dataset has 'url' column
if 'url' in df.columns:
    # Adjust 'label' to your column name (e.g., 'status', 'is_phishing', 'phishing')
    label_column = 'label'  # Change this based on data.csv
    if label_column not in df.columns:
        print(f"Error: '{label_column}' column not found. Available columns:", df.columns.tolist())
        exit(1)
    X = np.array([extract_features(url) for url in df['url']])
    y = df[label_column]
else:
    # If dataset has pre-extracted features
    feature_columns = [
        'length_url', 'length_hostname', 'nb_dots', 'nb_hyphens', 'nb_at', 'nb_qm',
        'nb_and', 'nb_eq', 'nb_underscore', 'nb_tilde', 'nb_percent', 'nb_slash',
        'nb_colon', 'nb_comma', 'nb_semicolumn', 'nb_dollar', 'nb_space', 'nb_www',
        'nb_com', 'nb_dslash', 'ratio_digits_url', 'ratio_digits_host'
    ]
    missing_cols = [col for col in feature_columns if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing feature columns: {missing_cols}")
        exit(1)
    X = df[feature_columns].values
    label_column = 'label'  # Change this based on data.csv
    if label_column not in df.columns:
        print(f"Error: '{label_column}' column not found. Available columns:", df.columns.tolist())
        exit(1)
    y = df[label_column]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

# Save model
joblib.dump(model, 'model.pkl')  # Save in Model directory
print("Model saved to model.pkl")