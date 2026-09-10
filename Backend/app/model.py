import joblib
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model= joblib.load(os.path.join(BASE_DIR, "model.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "scaler.pkl"))
feature_names = joblib.load(os.path.join(BASE_DIR, "feature_names.pkl"))

def predict(features: dict):
	try:
		input_values = [features[name] for name in feature_names]
	except KeyError as e:
		raise ValueError(f"Missing feature: {e}")

	input_df =pd.DataFrame([input_values], columns=feature_names)
	input_scaled = scaler.transform(input_df)


	prediction = model.predict(input_scaled)[0]
	probability = model.predict_proba(input_scaled)[0][1] 

	return {
		"diagnosis": "Malignant" if prediction == 1 else "Benign",
		"malignant_probability" : round(float(probability), 4)
		}
