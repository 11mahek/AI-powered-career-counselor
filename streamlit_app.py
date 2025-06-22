import streamlit as st
from huggingface_hub import InferenceClient
import os

# Initialize session state variables if not already done
if "step" not in st.session_state:
    st.session_state.step = 0
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

# Hugging Face inference client setup
client = InferenceClient(
    provider="nscale",
    api_key=os.environ["hf_token"],
)

# Title and subtitle
st.title("\U0001F393 AI-Powered Career Counselor")
st.markdown("Answer a few smart questions and let AI guide your future!")

# Step 0: Ask for age and interest
if st.session_state.step == 0:
    age = st.number_input("Enter your age:", min_value=10, max_value=100, key="age")
    interest = st.text_input("What are your interests? (e.g., technology, art, science)", key="interest")
    if st.button("Start Quiz") and interest:
        st.session_state.step = 1
        st.rerun()

# Step 1: Generate questions using the AI
elif st.session_state.step == 1:
    prompt = (
        f"Generate 5 multiple choice questions for a career quiz for a {st.session_state.age}-year-old "
        f"interested in {st.session_state.interest}. Each question should be clearly formatted like:\n"
        f"Q: [Question Text]\nA) Option 1\nB) Option 2\nC) Option 3\nD) Option 4"
    )

    with st.spinner("Generating your custom quiz..."):
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()

        # Parse questions
        blocks = result.split("Q: ")
        questions = []
        for block in blocks[1:]:
            lines = block.strip().split("\n")
            question_text = lines[0].strip()
            options = [line[3:].strip() for line in lines[1:5]]
            questions.append({
                "question": question_text,
                "options": options
            })

        st.session_state.questions = questions
        st.session_state.step = 2
        st.session_state.current_q = 0
        st.session_state.answers = []
        st.rerun()

# Step 2: Show one question at a time
elif st.session_state.step == 2:
    q = st.session_state.questions[st.session_state.current_q]
    st.markdown(f"**Question {st.session_state.current_q + 1}: {q['question']}**")

    answer = st.radio("Choose an answer:", ["A", "B", "C", "D"], key=f"q_{st.session_state.current_q}")

    if st.button("Next"):
        st.session_state.answers.append(answer)
        st.session_state.current_q += 1

        if st.session_state.current_q >= len(st.session_state.questions):
            st.session_state.step = 3
        st.rerun()

# Step 3: Show summary or result (placeholder)
elif st.session_state.step == 3:
    st.success("🎉 Quiz Completed!")
    st.write("You selected:")
    for idx, ans in enumerate(st.session_state.answers):
        st.write(f"Q{idx+1}: {ans}")

    # Restart option
    if st.button("Restart Quiz"):
        st.session_state.step = 0
        st.session_state.answers = []
        st.session_state.questions = []
        st.rerun()
