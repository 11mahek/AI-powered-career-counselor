import streamlit as st
from huggingface_hub import InferenceClient

# Load HF token from secrets
HF_TOKEN = st.secrets["HF_TOKEN"]

# Setup LLaMA 3.1 client
client = InferenceClient(
    provider="nscale",
    api_key=HF_TOKEN,
)

st.set_page_config(page_title="AI Career Counselor 💡", layout="centered")
st.title("🎓 AI-Powered Career Counselor")
st.write("Answer a few smart questions and let AI guide your future!")

# State setup
if "step" not in st.session_state:
    st.session_state.step = 0
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []

# STEP 0: Collect User Info
if st.session_state.step == 0:
    name = st.text_input("👤 Your Name")
    age = st.slider("🎂 Your Age", 10, 30, 17)
    interest = st.text_input("💭 What are your interests? (e.g., technology, creativity, business)")

    if st.button("🚀 Start Quiz"):
        st.session_state.name = name
        st.session_state.age = age
        st.session_state.interest = interest
        st.session_state.step = 1

# STEP 1: Generate Quiz
elif st.session_state.step == 1:
    with st.spinner("Creating personalized quiz..."):
        prompt = (
            f"Create 3 short and fun multiple-choice questions for a career interest quiz for a {st.session_state.age}-year-old "
            f"interested in {st.session_state.interest}. Each question should have 4 options (A, B, C, D). Format as:\n"
            f"Q1: <question>\nA. ...\nB. ...\nC. ...\nD. ...\n\nQ2: ..."
        )

        try:
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content
            st.session_state.questions = result.strip().split("\n\n")
            st.session_state.step = 2

        except Exception as e:
            st.error(f"❌ Failed to generate quiz: {str(e)}")

# STEP 2: Show Questions
elif st.session_state.step == 2:
    current_q = len(st.session_state.answers)
    if current_q < len(st.session_state.questions):
        st.markdown(f"**{st.session_state.questions[current_q]}**")
        answer = st.radio("Choose an option:", ["A", "B", "C", "D"], key=f"q{current_q}")

        if st.button("Next"):
            st.session_state.answers.append(answer)

            if len(st.session_state.answers) < len(st.session_state.questions):
                st.rerun()
            else:
                st.session_state.step = 3
    else:
        st.session_state.step = 3

# STEP 3: Move to career suggestion (next phase)
elif st.session_state.step == 3:
    st.success("✅ Quiz completed!")
    st.write("Click below to see your career recommendation.")
    if st.button("🎯 Get Career Suggestion"):
        st.session_state.step = 4
