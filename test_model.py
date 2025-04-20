import joblib
import os
path = 'Model/model.pkl'
abs_path = os.path.abspath(path)
print("Relative path:", path)
print("Absolute path:", abs_path)
print("File exists:", os.path.exists(abs_path))
print("File readable:", os.access(path, os.R_OK))
model = joblib.load(path)
print("Model loaded successfully")