import os
import streamlit as st
from huggingface_hub import InferenceClient
from fpdf import FPDF
import base64
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
    st.session_state.suggest_career = ""

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
        f"Generate 3 multiple-choice questions for a person who completely confused in his life."
        f"for a {st.session_state.age}-year-old interested in {st.session_state.interest}. "
        "we can easily suggest him best future career. "
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
    if st.button("Career"):
        prompt = (
            f"Based on these answers {st.session_state.answers}, the user is a {st.session_state.age}-year-old "
            f"interested in {st.session_state.interest}. Suggest 4-5 most suitable career paths with market trends and reasons for each."
            "Show Market trend and Reason on different separate paragraph format for good presentation"
        )
        with st.spinner("Analyzing your answer..."):
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",  
                messages=[{"role": "user", "content": prompt}]
            ) 
            result = response.choices[0].message.content.strip()
            st.session_state.suggest_career = result
            st.session_state.step = 4
        st.rerun()  
# Step 4: Display career suggestions and Skill Gap button
elif st.session_state.step == 4:
    st.subheader("📊 Career Analysis Based on Your Answers:")
    
    st.markdown("### 🌱 Help Us Understand You Better")
    st.markdown("_This will improve the Skill Gap Analyzer output. And helpful for us._")

    # Collect additional info
    st.session_state.book_preference = st.text_input("📚 What type of books do you like to read?")
    st.session_state.hobbies = st.text_input("🎨 What are your hobbies?")
    st.session_state.upskill_activities = st.text_input("📈 How do you upskill yourself?")
    st.session_state.side_interests = st.text_input("🌱 Any other interests?")

    st.markdown("### 🔍 Want deeper insights?")
    st.markdown("Click below to analyze your **Skill Gaps** based on your answers, interests, and habits.")

    if st.button("🔍 Analyze Skill Gaps"):
        prompt = (
            f"The user is {st.session_state.age} years old and interested in {st.session_state.interest}. "
            f"They answered the quiz with: {st.session_state.answers}.\n\n"
            f"Additional background:\n"
            f"- Regular upskilling habits: {st.session_state.upskill_activities}\n"
            f"- Hobbies: {st.session_state.hobbies}\n"
            f"- Side interests: {st.session_state.side_interests}\n"
            f"- Preferred book genres: {st.session_state.book_preference}\n\n"
            f"Based on the following career suggestions:\n{st.session_state.suggest_career}\n\n"
            f"Please analyze the required skills for each career and compare with user's answers and interest. "
            f"Provide a breakdown like:\n\n"
            f"- Career: X\n"
            f"- Required Skills: ...\n"
            f"- Likely Skills User Has: ...\n"
            f"- Missing Skills: ..."
        )

        with st.spinner("Analyzing Skill Gaps..."):
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{'role': 'user', 'content': prompt}]
            )
            skill_analysis = response.choices[0].message.content.strip()
            st.session_state.skill_gap = skill_analysis
            st.session_state.step = 5
        st.rerun()

    st.markdown("### 📄 Suggested Career Paths")
    st.markdown("_(Scroll to review full suggestions)_")
    st.markdown(st.session_state.suggest_career)
    st.markdown("---")

# Step 5: Display Skill Gap Analysis
elif st.session_state.step == 5:
    st.subheader("🧠 Skill Gap Analyzer Result")
    
    # ✨ NEW: Ask user's final career goal right away
    st.markdown("### 🎯 Now it's your turn!")
    st.markdown("Tell us what career you're most interested in now, and we'll generate a personalized roadmap for you.")
    career_goal = st.text_input("Personalized Your career...")

    if st.button("📍 Generate My Personalized Roadmap") and career_goal:
        prompt = (
            f"The user is {st.session_state.age} years old and interested in {st.session_state.interest}. "
            f"They answered the quiz with: {st.session_state.answers}. "
            f"Their current goal is to become a {career_goal}. "
            "Please create a complete personalized roadmap for this goal including:\n"
            "- Skills to learn (with order)\n"
            "- Tools/Technologies to master\n"
            "- Recommended courses or platforms (free/paid)\n"
            "- Real-world projects to build\n"
            "- Estimated timeline (beginner to job-ready)\n"
            "- Certifications if needed\n"
            "- Any bonus tips or habits for success"
        )
        with st.spinner("Generating your roadmap..."):
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": prompt}]
            )
            roadmap = response.choices[0].message.content.strip()
            st.session_state.roadmap = roadmap
            st.session_state.step = 6
        st.rerun()

    # Now show skill gap AFTER the roadmap input
    st.markdown("---")
    st.markdown("### 🔍 Skill Gap Breakdown") 
    st.markdown("Here's a breakdown based on your answers and suggestions:")
    st.markdown(st.session_state.skill_gap)

elif st.session_state.step == 6:
    st.subheader("📍 Your Personalized Career Roadmap")
    st.markdown("Follow this guide to reach your goal step by step:")

    # Show roadmap inside an expander
    with st.expander("📋 Click to view your complete roadmap"):
        st.markdown(st.session_state.roadmap)

    # PDF Generation Code
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(200, 10, "Your Personalized Career Roadmap", ln=True, align="C")
        def chapter_body(self, text):
            self.set_font("Arial", "", 12)
            self.multi_cell(0, 10, text)

    pdf = PDF()
    pdf.add_page()
    pdf.chapter_body(st.session_state.roadmap)
    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_output).decode()
    st.markdown(
        f'<a href="data:application/octet-stream;base64,{b64}" download="My_Career_Roadmap.pdf">'
        f'📥 <button style="background-color:#4CAF50;color:white;padding:10px;border:none;border-radius:5px;">Download Roadmap as PDF</button>'
        f'</a>',
        unsafe_allow_html=True
    )

    # BONUS SECTION: Personality Insight from AI
    st.markdown("---")
    st.markdown("### 🧠 AI Personality Insight")
    if "personality" not in st.session_state:
        prompt = (
            f"The user is {st.session_state.age} years old, interested in {st.session_state.interest}. "
            f"They answered the quiz with: {st.session_state.answers}. "
            f"The user also mentioned they like to read "
            f"{st.session_state['book_preference'] if 'book_preference' in st.session_state else 'not specified'} books, "
            f"regularly do {st.session_state['hobbies'] if 'hobbies' in st.session_state else 'not specified'}, "
            f"upskill through {st.session_state['upskill_activities'] if 'upskill_activities' in st.session_state else 'not specified'}, "
            f"and have side interests in {st.session_state['side_interests'] if 'side_interests' in st.session_state else 'not specified'}. "
            f"Based on this, generate a brief personality insight about the user (2-3 lines) "
            f"that describes their mindset, behavior, and potential career traits."
        )
        
        with st.spinner("Analyzing your personality..."):
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{'role': 'user', 'content': prompt}]
            )
            st.session_state.personality = response.choices[0].message.content.strip()

    st.success(st.session_state.personality)

    # Optional motivational tips
    with st.expander("💡Believe yourself and Trust your Fate"):
        st.markdown("🚀 Stay consistent, build projects, and follow industry trends...")
        st.markdown("🎯 Network with professionals on LinkedIn and explore internships early.")
        st.markdown("🧠 Focus on both technical and soft skills.")

    # Restart Option
    if st.button("🔄 Restart Journey"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
