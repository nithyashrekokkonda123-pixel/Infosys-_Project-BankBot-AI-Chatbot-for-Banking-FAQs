import joblib
import os
import re
import numpy as np

MODEL_DIR = "models/intent_model"

model = joblib.load(os.path.join(MODEL_DIR, "intent_model.pkl"))
vectorizer = joblib.load(os.path.join(MODEL_DIR, "vectorizer.pkl"))
encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))

def predict_intents(text, top_n=3):
    # Split combined queries
    parts = re.split(r'\band\b|\?|\.|,', text.lower())
    parts = [p.strip() for p in parts if p.strip()]

    intent_scores = {intent: 0.0 for intent in encoder.classes_}

    # Accumulate probabilities per intent
    for part in parts:
        X = vectorizer.transform([part])
        probs = model.predict_proba(X)[0]

        for i, p in enumerate(probs):
            intent = encoder.inverse_transform([i])[0]
            intent_scores[intent] += float(p)

    
    detected_intents = set()
    for part in parts:
        X = vectorizer.transform([part])
        probs = model.predict_proba(X)[0]
        best_idx = int(probs.argmax())
        detected_intents.add(encoder.inverse_transform([best_idx])[0])

    # Zero out non-detected intents
    for intent in intent_scores:
        if intent not in detected_intents:
            intent_scores[intent] = 0.0

    scores = np.array(list(intent_scores.values()))

    # Normalize 
    if scores.sum() > 0:
        scores = scores / scores.sum()

    results = []
    for intent, score in zip(intent_scores.keys(), scores):
        results.append({
            "intent": intent,
            "confidence": round(float(score), 2)
        })

    # Sort by confidence
    results = sorted(results, key=lambda x: x["confidence"], reverse=True)

    return results