import streamlit as st
import re
from huggingface_hub import InferenceClient

# Initialize the Inference Client
client = InferenceClient(
    model="meta-llama/Llama-3.1-8B-Instruct",
    token=st.secrets["hf_token"]
)

# Page Setup
st.set_page_config(page_title="AI-Powered Career Counselor", layout="centered")
st.title("🎓 AI-Powered Career Counselor")
st.markdown("Answer a few smart questions and let AI guide your future!")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.age = None
    st.session_state.interest = None
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.current_question = 0

# Step 0 – Input Age and Interest
if st.session_state.step == 0:
    st.session_state.age = st.number_input("Your Age", min_value=10, max_value=100, value=17)
    st.session_state.interest = st.text_input("What are you interested in? (e.g., tech, art, sports)")
    if st.button("Start Quiz") and st.session_state.interest:
        st.session_state.step = 1
        st.rerun()

# Step 1 – Generate Quiz
elif st.session_state.step == 1:
    prompt = (
        f"Generate 3 short, fun multiple choice questions for a career quiz "
        f"for a {st.session_state.age}-year-old interested in {st.session_state.interest}. "
        f"Each question should have 4 options labeled A), B), C), D), each on its own line."
    )
    with st.spinner("🤖 Generating your custom quiz..."):
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()

    # Parse questions using regex
    raw_blocks = re.findall(r"Q\d+:.*?(?=Q\d+:|$)", result, re.DOTALL)
    parsed_questions = []
    for block in raw_blocks:
        lines = block.strip().split("\n")
        question_text = lines[0].strip()
        options = [line.strip() for line in lines[1:] if line.strip()]
        parsed_questions.append({
            "question": question_text,
            "options": options
        })

    st.session_state.questions = parsed_questions
    st.session_state.step = 2
    st.experimental_rerun()

# Step 2 – Display Quiz
elif st.session_state.step == 2:
    q_num = st.session_state.current_question
    total_q = len(st.session_state.questions)

    if q_num < total_q:
        q = st.session_state.questions[q_num]
        st.markdown(f"**{q['question']}**")

        if q['options']:
            answer = st.radio("Choose an answer:", q['options'], key=f"q{q_num}")
            if st.button("Next"):
                st.session_state.answers.append(answer)
                st.session_state.current_question += 1
                st.experimental_rerun()
        else:
            st.warning("⚠️ Options not found for this question.")
    else:
        st.session_state.step = 3
        st.rerun()

# Step 3 – Show Completion Message
elif st.session_state.step == 3:
    st.success("🎉 You've completed the quiz!")
    st.write("Your answers:")
    for i, a in enumerate(st.session_state.answers, 1):
        st.write(f"Q{i}: {a}")
    st.button("Restart", on_click=lambda: st.session_state.clear())
