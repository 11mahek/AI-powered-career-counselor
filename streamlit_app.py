import os
import streamlit as st
from huggingface_hub import InferenceClient

# Setup the client
client = InferenceClient(
    provider="nscale",
    api_key=st.secrets["hf_token"],
)

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 0
if "age" not in st.session_state:
    st.session_state.age = ""
if "interest" not in st.session_state:
    st.session_state.interest = ""
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0

# Step 0: Get user input
if st.session_state.step == 0:
    st.title("🎓 AI-Powered Career Counselor")
    st.write("Answer a few smart questions and let AI guide your future!")

    st.session_state.age = st.text_input("Enter your age:")
    st.session_state.interest = st.text_input("What are you interested in?")

    if st.button("Start Quiz") and st.session_state.age and st.session_state.interest:
        st.session_state.step = 1
        st.experimental_rerun()

# Step 1: Generate quiz
elif st.session_state.step == 1:
    prompt = (
        f"Generate 3 short, fun multiple choice questions for a career quiz "
        f"for a {st.session_state.age}-year-old interested in {st.session_state.interest}. "
        f"Each question should have 4 options labeled A), B), C), D)."
    )
    with st.spinner("Generating your custom quiz..."):
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()

        # Clean and split into questions
        question_blocks = [q.strip() for q in result.split("\n\n") if "A)" in q]
        st.session_state.questions = question_blocks
        st.session_state.step = 2
        st.session_state.current_question = 0
        st.session_state.answers = []
        st.experimental_rerun()

# Step 2: Display questions one by one
elif st.session_state.step == 2:
    if st.session_state.current_question < len(st.session_state.questions):
        q = st.session_state.questions[st.session_state.current_question]
        parts = q.split("A)")
        question_text = parts[0].strip()
        options_block = "A)" + parts[1] if len(parts) > 1 else ""
        options = [opt.strip() for opt in options_block.split("\n") if opt.strip()]

        st.markdown(f"**Question {st.session_state.current_question + 1}:** {question_text}")
        selected_option = st.radio("Choose an answer:", ["A", "B", "C", "D"], key=st.session_state.current_question)

        if st.button("Next"):
            st.session_state.answers.append(selected_option)
            st.session_state.current_question += 1
            st.experimental_rerun()
    else:
        st.session_state.step = 3
        st.experimental_rerun()

# Step 3: Show results
elif st.session_state.step == 3:
    st.success("🎉 Quiz Completed!")
    st.write("Your answers:", st.session_state.answers)
    st.write("You can now add logic to generate career recommendations based on your answers!")
