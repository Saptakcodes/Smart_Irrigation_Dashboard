import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib 

# Load dataset
df = pd.read_csv("updated_dataset_without_crop.csv")  # Ensure this file is in the same directory

# Features and target
X = df.drop("pump_on", axis=1)
y = df["pump_on"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Random Forest Model
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    class_weight='balanced',
    random_state=42
)

# Train and Predict
rf_model.fit(X_train, y_train)
y_pred = rf_model.predict(X_test)

joblib.dump(rf_model, "irrigation_model.pkl")
joblib.dump(list(X.columns), "irrigation_features.pkl")

# Accuracy and Evaluation
accuracy = accuracy_score(y_test, y_pred)
print("Random Forest Model")
print("--------------------")
print(f"Accuracy: {accuracy:.4f}")
print("Classification Report:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
