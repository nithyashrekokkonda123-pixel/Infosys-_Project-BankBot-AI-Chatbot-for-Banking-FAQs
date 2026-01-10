import streamlit as st
import json
import os
import subprocess
from pathlib import Path

from nlu_engine.infer_intent import predict_intents
from nlu_engine.entity_extractor import EntityExtractor

INTENTS_PATH = "nlu_engine/intents.json"
MODEL_DIR = "models/intent_model"

st.set_page_config(page_title="BankBot NLU", layout="wide")
st.markdown("""
<style>
/* Overall background */
.stApp {
    background: linear-gradient(
        135deg,
        #eef2ff,
        #f8fbff,
        #eaf4ff
    );
}

/* Titles */
h1, h2, h3 {
    color: #1f2a44;
    font-family: 'Segoe UI', sans-serif;
}

/* Text areas & inputs */
textarea, input {
    background-color: #ffffff !important;
    border-radius: 8px !important;
    border: 1px solid #d0d7e2 !important;
}

/* Buttons */
button {
    background-color: #1f77ff !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
button:hover {
    background-color: #155edc !important;
}

/* Intent cards */
.intent-card {
    background: linear-gradient(135deg, #e6f0ff, #ffffff);
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #cfe0ff;
    margin-bottom: 8px;
}

/* Confidence badge */
.confidence-badge {
    background-color: #1f77ff;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
}

/* Entity cards */
.entity-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid #e0e6ef;
    margin-bottom: 6px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #1f2a44;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


def load_intents():
    with open(INTENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_intents(data):
    with open(INTENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def model_exists():
    return os.path.exists(MODEL_DIR) and any(Path(MODEL_DIR).iterdir())



st.title("Kokkonda Nithyashre")
st.title("BankBot NLU Engine")

col1, col2 = st.columns([1, 1.3])



with col1:
    st.subheader("Intents (edit & add)")
    intents_data = load_intents()

    for intent in intents_data["intents"]:
        with st.expander(f"{intent['name']} ({len(intent['examples'])} examples)"):
            text = st.text_area(
                "Edit examples",
                "\n".join(intent["examples"]),
                key=intent["name"]
            )
            intent["examples"] = text.split("\n")

    st.subheader("Create new intent")
    name = st.text_input("Intent name")
    examples = st.text_area("Examples (one per line)")

    if st.button("Add Intent"):
        if name.strip():
            intents_data["intents"].append({
                "name": name.strip(),
                "examples": examples.split("\n")
            })
            save_intents(intents_data)
            st.success(" Intent added!")



with col2:
    st.subheader("NLU Visualizer")

    query = st.text_area("User Query:")
    top_k = st.number_input("Top intents to show", 1, 10, 4)

    if st.button("Analyze"):
        
        st.subheader("Intent Recognition")
        intents = predict_intents(query)
        intents = sorted(intents, key=lambda x: x["confidence"], reverse=True)
        intents = intents[:top_k]

        for i in intents:

            st.markdown(
                f"""
                <div style='display:flex; justify-content:space-between; 
                            align-items:center;
                            padding:10px; background:#f0f0f0; 
                            border-radius:10px; margin-bottom:5px;
                            border:1px solid #ccc;'>
                    <span style='font-size:15px; font-weight:500;'>{i['intent']}</span>
                    <span style='background:#d0e7ff; padding:3px 10px; 
            border-radius:15px; color:#0b3d91; font-weight:600;'>{float(i['confidence']):.2f}</span>
                </div>
                """,
                unsafe_allow_html=True
            )



st.divider()
st.subheader("Entity Extraction")               
extractor = EntityExtractor()
entities = extractor.extract(query)
if entities:
    for ent in entities:
        st.markdown(
            f"""
            <div style='display:flex; justify-content:space-between; 
                        align-items:center;
                        padding:10px; background:#f9f9f9; 
                        border-radius:10px; margin-bottom:5px;
                        border:1px solid #ddd;'>
                <span style='font-size:15px; font-weight:500;'>{ent['entity']}</span>
                <span style='font-size:14px; color:#555;'>{ent['value']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No entities found.")



st.divider()
st.subheader("Train Model")

epochs = st.number_input("Epochs", 1, 50, 3)
batch = st.number_input("Batch size", 8, 64, 8)
lr = st.number_input("Learning rate", value=0.00002, format="%.5f")

if model_exists():
    st.success("Trained model found")
else:
    st.warning(" No trained model")

if st.button("Start Training"):
    subprocess.Popen([
        "python", "nlu_engine/train_intent.py",
        "--epochs", str(epochs),
        "--batch_size", str(batch),
        "--lr", str(lr)
    ])
    st.success(" Training started!")
