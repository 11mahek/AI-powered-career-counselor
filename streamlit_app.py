import os
import streamlit as st
from huggingface_hub import InferenceClient

# Hugging Face Token from secrets
HF_TOKEN = st.secrets["hf_token"]

client = InferenceClient(provider="nscale", api_key=HF_TOKEN)

st.set_page_config(page_title="AI-Powered Career Counselor", page_icon="🎓")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.age = ""
    st.session_state.interest = ""
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.current_q = 0

st.title("🎓 AI-Powered Career Counselor")
st.write("Answer a few smart questions and let AI guide your future!")

# Step 0: Ask for age and interest
if st.session_state.step == 0:
    st.session_state.age = st.text_input("Enter your age", placeholder="e.g., 17")
    st.session_state.interest = st.text_input("Enter your area of interest", placeholder="e.g., Technology, Arts, Business")

    if st.button("Start Quiz"):
        if st.session_state.age and st.session_state.interest:
            st.session_state.step = 1
            st.rerun()
        else:
            st.warning("Please enter both age and interest.")

# Step 1: Generate quiz
elif st.session_state.step == 1:
    prompt = (
        f"Generate multiple-choice questions for a person who completely confused in his life and person age is {st.session_state.age}"
        f"for a {st.session_state.age}-year-old interested in {st.session_state.interest}. "
        "Generate enough multiple-choice questions so, we can easily suggest him best future career. "
        f"Each question should be standalone and include 4 answer options labeled A, B, C, and D. "
        f"Format the output as:\n"
        f"Q: <question text>\nA: <option 1>\nB: <option 2>\nC: <option 3>\nD: <option 4>\n"
    )

    with st.spinner("Generating your custom quiz..."):
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()

        # Split questions
        raw_qs = [q.strip() for q in result.split("Q: ") if q.strip()]
        parsed = []
        for q in raw_qs:
            lines = q.split("\n")
            question_text = lines[0]
            options = {opt[0]: opt[3:].strip() for opt in lines[1:] if opt and opt[1] == ":"}
            parsed.append({"question": question_text, "options": options})

        st.session_state.questions = parsed
        st.session_state.step = 2
        st.rerun()

# Step 2: Show quiz one by one
elif st.session_state.step == 2:
    q_idx = st.session_state.current_q
    questions = st.session_state.questions
    if q_idx < len(questions):
        q = questions[q_idx]
        op = []
        st.write(f"**Question {q_idx + 1}: {q['question']}**")
        for key, value in q['options'].items():
            op.append(f"{key}) {value}")

        selected = st.radio("Choose an answer:", op, key=f"q{q_idx}")

        if st.button("Next"):
            st.session_state.answers.append(selected)
            st.session_state.current_q += 1
            st.rerun()
    else:
        st.session_state.step = 3
        st.rerun()

# Step 3: Completion
elif st.session_state.step == 3:
    st.success("🎉 You’ve completed the quiz!")
    st.write("Your answers:", st.session_state.answers)

    if st.button("Restart"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
