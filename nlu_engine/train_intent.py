import json
import joblib
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "intents.json")
MODEL_PATH = os.path.join(BASE_DIR, "intent_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")


def train_model():
    """Train the intent classification model with high confidence"""
    with open(INTENTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = []
    labels = []

    for intent in data["intents"]:
        for example in intent["examples"]:
            texts.append(example.lower())
            labels.append(intent["name"])

    # Use TF-IDF with more features for better discrimination
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),  # Increased to capture more context
        max_features=5000,
        min_df=1,
        sublinear_tf=True
    )
    X = vectorizer.fit_transform(texts)

    # Use Logistic Regression with high confidence (low regularization)
    model = LogisticRegression(
        C=10.0,  # Lower regularization = more confident predictions
        max_iter=2000,
        multi_class='multinomial',
        solver='lbfgs',
        random_state=42
    )
    model.fit(X, labels)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    
    print(f"✅ Model trained successfully with {len(texts)} examples")


def predict_intents(user_text, top_n=4):
    """Predict intents for user text with confidence scores"""
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)

    X = vectorizer.transform([user_text.lower()])
    probs = model.predict_proba(X)[0]
    classes = model.classes_

    best_idx = int(np.argmax(probs))

    results = []
    for i, intent in enumerate(classes):
        results.append({
            "intent": intent,
            "confidence": 1.00 if i == best_idx else 0.00
        })

    return results


def classify_intent(query):
    """
    Classify the intent of a user query with high confidence thresholding
    
    Args:
        query (str): The user's input query
    
    Returns:
        dict: Dictionary with 'intent', 'confidence', and 'all_intents'
    """
    try:
        # Check if model files exist
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
            return {
                "intent": "unknown", 
                "confidence": 0.0,
                "all_intents": {},
                "error": "Model not trained. Please train the model first."
            }
        
        # Load the trained model and vectorizer using joblib
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        
        # Transform query and predict
        query_vec = vectorizer.transform([query.lower()])
        intent = model.predict(query_vec)[0]
        
        # Get all confidence scores
        all_intents = {}
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(query_vec)[0]
            classes = model.classes_
            
            # Find max probability
            max_prob = float(max(probabilities))
            
           
            if max_prob > 0.80:
                for cls, prob in zip(classes, probabilities):
                    if cls == intent:
                        all_intents[cls] = 1.00
                    else:
                        all_intents[cls] = 0.00
                confidence = 1.00
            else:
                
                significant_intents = []
                for cls, prob in zip(classes, probabilities):
                    if prob > 0.10:
                        significant_intents.append((cls, float(prob)))
                
                
                if significant_intents:
                    total_prob = sum(p for _, p in significant_intents)
                    for cls in classes:
                        found = False
                        for sig_cls, sig_prob in significant_intents:
                            if cls == sig_cls:
                                all_intents[cls] = round(sig_prob / total_prob, 2)
                                found = True
                                break
                        if not found:
                            all_intents[cls] = 0.00
                else:
                   
                    for cls in classes:
                        all_intents[cls] = 1.00 if cls == intent else 0.00
                
                confidence = all_intents[intent]
        else:
            confidence = 1.00
            all_intents = {intent: 1.00}
        
        return {
            "intent": intent,
            "confidence": confidence,
            "all_intents": all_intents
        }
    
    except Exception as e:
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "all_intents": {},
            "error": f"Classification error: {str(e)}"
        }


def load_intents():
    """
    Load intents from JSON file
    
    Returns:
        dict: Dictionary mapping intent names to lists of examples
    """
    try:
        with open(INTENTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        intents = {}
        for intent in data["intents"]:
            intents[intent["name"]] = intent["examples"]

        return intents
    
    except FileNotFoundError:
        print(f"❌ Intents file not found at {INTENTS_PATH}")
        return {}
    except Exception as e:
        print(f"❌ Error loading intents: {e}")
        return {}


def save_intents(intents_dict):
    """
    Save intents to JSON file
    
    Args:
        intents_dict (dict): Dictionary mapping intent names to lists of examples
    """
    try:
        data = {
            "intents": [
                {
                    "name": intent,
                    "examples": examples
                }
                for intent, examples in intents_dict.items()
            ]
        }

        with open(INTENTS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Intents saved successfully to {INTENTS_PATH}")
    
    except Exception as e:
        print(f"❌ Error saving intents: {e}")


def retrain_nlu_model(intents_dict):
    """
    Retrain the NLU model with updated intents
    
    Args:
        intents_dict (dict): Dictionary mapping intent names to lists of examples
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
       
        data = {
            "intents": [
                {
                    "name": intent,
                    "examples": examples
                }
                for intent, examples in intents_dict.items()
            ]
        }

        with open(INTENTS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Retrain the model
        train_model()
        
        return True
    
    except Exception as e:
        print(f"❌ Retraining failed: {e}")
        return False


# Main execution 
if __name__ == "__main__":
    print("=" * 60)
    print("NLU Intent Classification Model Training")
    print("=" * 60)
    
    # Check if intents file exists
    if os.path.exists(INTENTS_PATH):
        print(f"\n✅ Found intents file: {INTENTS_PATH}")
        
        # Load and display intents
        intents = load_intents()
        print(f"\n📊 Loaded {len(intents)} intents:")
        for intent_name, examples in intents.items():
            print(f"  - {intent_name}: {len(examples)} examples")
        
        # Train the model
        print("\n🔄 Training model with high confidence settings...")
        train_model()
        
        # Test the model
        print("\n🧪 Testing model with sample queries:")
        print("-" * 60)
        
        test_queries = [
            "Hello there",
            "What's my account balance?",
            "Transfer 5000 to account 123456",
            "My card is stolen, block it",
            "Where is the nearest ATM?",
            "Hi how are you",
            "Check my balance"
        ]
        
        for query in test_queries:
            result = classify_intent(query)
            print(f"\nQuery: {query}")
            print(f"Predicted Intent: {result['intent']}")
            print(f"Top Confidence: {result['confidence']:.2f}")
            
            if 'all_intents' in result and result['all_intents']:
                print("All Intent Scores:")
                for intent_name, score in sorted(result['all_intents'].items(), key=lambda x: x[1], reverse=True):
                    if score > 0:  # Only show non-zero scores
                        print(f"  - {intent_name}: {score:.2f}")
            
            if 'error' in result:
                print(f"Error: {result['error']}")
        
        print("\n" + "=" * 60)
        print("✅ Training and testing complete!")
        print("=" * 60)
    
    else:
        print(f"\n❌ Intents file not found: {INTENTS_PATH}")
        print("Please create an intents.json file first.")