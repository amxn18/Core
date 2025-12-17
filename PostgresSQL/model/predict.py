import pickle
import pandas as pd
# Import ML Model
with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

MODEL_VERSION = "1.0.0"

classLabels = model.classes_.tolist()  # Labels for prediction output (high, medium, low)
def predictOutput(userInput : dict) -> str:
    inputDf = pd.DataFrame([userInput]) 
    output = model.predict(inputDf)[0]
    probabilities = model.predict_proba(inputDf)[0]
    confidence = max(probabilities)

    # Mapping 
    classProbs = dict(zip(classLabels, map(lambda p: round(p, 4), probabilities)))
    return {
        "predicted_category": output,
        "confidence": round(confidence, 4),
        "class_probabilities": classProbs
    }