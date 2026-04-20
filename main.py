import streamlit as st
import pandas as pd
import random
import os

# --- Load Data from CSV ---
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path)
    return df

CSV_FILE = "questions.csv"
df_questions = load_data(CSV_FILE)

# --- Session State Initialization ---
if 'subject' not in st.session_state:
    st.session_state.subject = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'user_choice' not in st.session_state:
    st.session_state.user_choice = None
if 'randomized_choices' not in st.session_state:
    st.session_state.randomized_choices = []

def reset_quiz():
    st.session_state.subject = None
    st.session_state.questions = []
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.submitted = False
    st.session_state.user_choice = None
    st.session_state.randomized_choices = []

def start_quiz(subject):
    st.session_state.subject = subject
    # Filter questions for the selected subject
    subject_df = df_questions[df_questions['Subject'] == subject]
    
    # Convert rows to a list of dictionaries for easier handling
    questions = []
    for _, row in subject_df.iterrows():
        questions.append({
            "question": row["Question"],
            "choices": [row["Choice1"], row["Choice2"], row["Choice3"], row["Choice4"]],
            "correct": row["CorrectAnswer"],
            "explanation": row["Explanation"]
        })
    
    random.shuffle(questions)
    st.session_state.questions = questions
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.submitted = False
    prepare_question()

def prepare_question():
    if st.session_state.current_index < len(st.session_state.questions):
        q = st.session_state.questions[st.session_state.current_index]
        choices = q["choices"].copy()
        random.shuffle(choices)
        st.session_state.randomized_choices = choices
        st.session_state.submitted = False
        st.session_state.user_choice = None

# --- UI Header ---
st.set_page_config(page_title="Subject Reviewer", page_icon="📚")
st.title("📚 Academic Subject Reviewer")

if df_questions is None:
    st.error(f"Error: {CSV_FILE} not found. Please ensure the CSV file exists in the project directory.")
else:
    # --- Landing Page ---
    if st.session_state.subject is None:
        st.subheader("Welcome! Please select a topic to begin your review.")
        topics = sorted(df_questions['Subject'].unique())
        selected_topic = st.selectbox("Choose a Subject:", topics)
        
        if st.button("Start Review"):
            start_quiz(selected_topic)
            st.rerun()

    # --- Quiz Page ---
    else:
        subject = st.session_state.subject
        questions = st.session_state.questions
        idx = st.session_state.current_index

        if idx < len(questions):
            q = questions[idx]
            
            st.write(f"**Subject:** {subject}")
            st.write(f"**Question {idx + 1} of {len(questions)}**")
            st.progress((idx) / len(questions))
            
            st.markdown(f"### {q['question']}")
            
            # Display options
            if not st.session_state.submitted:
                user_input = st.radio("Choose the correct answer:", st.session_state.randomized_choices, key=f"q_{idx}")
                if st.button("Submit Answer"):
                    st.session_state.user_choice = user_input
                    st.session_state.submitted = True
                    if user_input == q['correct']:
                        st.session_state.score += 1
                    st.rerun()
            else:
                # Show feedback
                user_choice = st.session_state.user_choice
                for choice in st.session_state.randomized_choices:
                    if choice == q['correct']:
                        st.success(f"✅ {choice} (Correct)")
                    elif choice == user_choice:
                        st.error(f"❌ {choice} (Your Answer)")
                    else:
                        st.write(f"⚪ {choice}")

                # Always show explanation
                st.info(f"**Explanation:** {q['explanation']}")
                
                if st.button("Next Question"):
                    st.session_state.current_index += 1
                    prepare_question()
                    st.rerun()

        else:
            # Results Page
            st.balloons()
            st.header("Review Completed!")
            st.write(f"Your final score: **{st.session_state.score} / {len(questions)}**")
            
            percentage = (st.session_state.score / len(questions)) * 100
            st.metric("Success Rate", f"{percentage:.1f}%")
            
            if st.button("Return to Landing Page"):
                reset_quiz()
                st.rerun()

# --- Sidebar ---
with st.sidebar:
    if st.session_state.subject:
        st.write(f"Current Review: **{st.session_state.subject}**")
        st.write(f"Score: {st.session_state.score}")
        if st.button("Quit Review"):
            reset_quiz()
            st.rerun()
    st.markdown("---")
    st.caption("Powered by Streamlit")
    st.info("Questions are loaded dynamically from `questions.csv`")
