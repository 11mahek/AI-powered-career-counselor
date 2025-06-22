import streamlit as st
from huggingface_hub import InferenceClient

# Load HF token from secrets
HF_TOKEN = st.secrets["hf_token"]

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
    prompt = (
        f"Generate 3 short, fun multiple choice questions for a career quiz "
        f"for a {st.session_state.age}-year-old interested in {st.session_state.interest}. "
        f"Each question should have 4 options labeled A), B), C), D)."
    )

    with st.spinner("Generating your custom quiz..."):
        try:
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content.strip()

            # Splitting the questions properly
            questions = [q.strip() for q in result.split("Q") if q.strip()]
            questions = [("Q" + q).strip() for q in questions]

            # Save and go to next step
            st.session_state.questions = questions
            st.session_state.step = 2
            st.rerun()

        except Exception as e:
            st.error(f"Error generating quiz: {e}")

# STEP 2: Show Questions
elif st.session_state.step == 2:
    current_q = len(st.session_state.answers)
    total_qs = len(st.session_state.questions)

    if current_q >= total_qs:
        st.session_state.step = 3
        st.rerun()

    q_text = st.session_state.questions[current_q]
    lines = q_text.split("\n")

    question = lines[0].strip()

    # Extract answer choices
    options = []
    for line in lines[1:]:
        line = line.strip()
        if line.startswith(("A", "B", "C", "D")):
            # Safely strip off "A)", "B)" etc.
            option = line[2:].strip() if ")" in line else line
            options.append(option)

    st.markdown(f"**{question}**")
    selected = st.radio("Choose an answer:", ["A", "B", "C", "D"], key=f"q{current_q}")

    if st.button("Next"):
        st.session_state.answers.append(selected)
        st.rerun()


# STEP 3: Move to career suggestion (next phase)
elif st.session_state.step == 3:
    st.success("✅ Quiz completed!")
    st.write("Click below to see your career recommendation.")
    if st.button("🎯 Get Career Suggestion"):
        st.session_state.step = 4
