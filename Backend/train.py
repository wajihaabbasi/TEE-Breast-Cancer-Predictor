import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn. metrics import accuracy_score, classification_report

df = pd.read_csv("data/data.csv")

# cleaning unnecessary columns
df = df.drop (columns=["id" , "Unnamed: 32"], errors = "ignore")
#setting the diagnosis to binary
df["diagnosis"] = df["diagnosis"].map({"M" : 1 , "B" : 0})

# Split features/target
X = df.drop(columns=["diagnosis"])
y = df["diagnosis"]

feature_names = X.columns.tolist()

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = LogisticRegression(max_iter=5000)
model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model.predict(X_test_scaled)
print("Accuracy:" , accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

joblib.dump(model, "app/model.pkl")
joblib.dump(scaler, "app/scaler.pkl")
joblib.dump(feature_names, "app/feature_names.pkl")

print("Saved model, scaler, and feature names to app")
