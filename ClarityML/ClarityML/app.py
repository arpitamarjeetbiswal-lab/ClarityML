import streamlit as st
import pickle
import numpy as np

# Load model and vectorizer
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "notebooks", "model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "notebooks", "vectorizer.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(vectorizer_path, "rb") as f:
    vectorizer = pickle.load(f)

def predict_with_confidence(text):
    vec = vectorizer.transform([text])
    probs = model.predict_proba(vec)[0]
    label = model.classes_[np.argmax(probs)]
    confidence = np.max(probs)
    return label, confidence

def important_words(text, label, top_n=5):
    vec = vectorizer.transform([text])
    feature_names = vectorizer.get_feature_names_out()
    class_index = model.classes_.tolist().index(label)
    coef = model.coef_[class_index]
    scores = vec.toarray()[0] * coef
    top_indices = scores.argsort()[-top_n:]
    return [feature_names[i] for i in top_indices]

def next_step(label):
    steps = {
        "confused": "Write down only one thing that matters right now.",
        "anxious": "Focus on what you can control today, not tomorrow.",
        "avoidant": "Start with a task that takes less than 5 minutes.",
        "clear": "Take the first concrete action toward your decision.",
        "motivated": "Use this energy to work for 25 focused minutes."
    }
    return steps[label]

# UI
st.title("ClarityML")
st.subheader("Turn confusion into clarity")

user_text = st.text_area("Write what's on your mind:")

if st.button("Analyze"):
    if user_text.strip():
        label, confidence = predict_with_confidence(user_text)
        words = important_words(user_text, label)
        step = next_step(label)

        st.markdown(f"### 🧠 Mental State: **{label}**")
        st.markdown(f"**Confidence:** {confidence:.2f}")

        st.markdown("**Key words influencing this:**")
        st.write(words)

        st.markdown("### 👉 Suggested next step")
        st.success(step)
    else:
        st.warning("Please enter some text.")
