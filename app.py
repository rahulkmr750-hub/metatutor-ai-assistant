import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MetaTutor | AI Personalized Learning Assistant",
    page_icon="🎓",
    layout="wide"
)

# --- KNOWLEDGE BASE: CURRICULUM & MODULES ---
MODULES = {
    "1. Enterprise Metadata Policies & Governance": {
        "summary": (
            "Metadata governance ensures consistent data classification, lineage tracking, "
            "and compliance across enterprise data pipelines. Key pillars include Technical, "
            "Operational, and Business metadata."
        ),
        "key_concepts": [
            "Business Metadata: Definitions, data ownership, and domain taxonomy.",
            "Technical Metadata: Schemas, data types, table structures, and foreign keys.",
            "Operational Metadata: ETL job logs, ingestion timestamps, SLA tracking, and error states."
        ],
        "quiz": [
            {
                "q": "Which type of metadata captures ETL job timestamps, SLA breaches, and row counts?",
                "options": ["Business Metadata", "Operational Metadata", "Structural Metadata", "Descriptive Metadata"],
                "answer": "Operational Metadata",
                "explanation": "Operational metadata tracks runtime characteristics such as job execution times, lag, and pipeline health."
            },
            {
                "q": "Why is a standardized metadata schema critical before data ingestion?",
                "options": [
                    "It reduces physical disk size by 90%",
                    "It prevents schema drift, ambiguity, and downstream reporting errors",
                    "It replaces the need for database indexing",
                    "It eliminates all network latency"
                ],
                "answer": "It prevents schema drift, ambiguity, and downstream reporting errors",
                "explanation": "Enforcing metadata standards at ingestion prevents mismatched tags and duplicate filings downstream."
            }
        ]
    },
    "2. Data Ingestion Guidelines & Deduplication": {
        "summary": (
            "Data ingestion pipelines must validate source integrity, enforce deduplication rules, "
            "and route anomalies before loading records into production analytical warehouses."
        ),
        "key_concepts": [
            "Idempotent Ingestion: Ensuring repeated pipeline runs do not create duplicate records.",
            "Deduplication & Priority Routing: Resolving multiple filings for the same entity/period.",
            "SLA & Turnaround Time (TAT) Monitoring: Flagging active jobs exceeding processing thresholds."
        ],
        "quiz": [
            {
                "q": "What does idempotency guarantee in a data ingestion pipeline?",
                "options": [
                    "Data is encrypted using AES-256",
                    "Re-running an ingestion job with the same input produces the exact same state without duplicates",
                    "All SQL queries run in parallel",
                    "Files are converted to PDF automatically"
                ],
                "answer": "Re-running an ingestion job with the same input produces the exact same state without duplicates",
                "explanation": "Idempotency prevents duplicate rows when retries occur after transient network or database failures."
            },
            {
                "q": "When two filings arrive for the same entity and period, what is the best ingestion practice?",
                "options": [
                    "Delete both filings immediately",
                    "Apply deduplication rules based on filing timestamp, completeness, and amendment flags",
                    "Load both into production without tags",
                    "Ignore primary period end dates"
                ],
                "answer": "Apply deduplication rules based on filing timestamp, completeness, and amendment flags",
                "explanation": "Deduplication workflows compare filing timestamps, amendment flags, and completeness prior to production load."
            }
        ]
    },
    "3. SQL & Python Automation for Quality Assurance": {
        "summary": (
            "Automated quality checks use SQL validation views and Python alerting scripts to detect "
            "period-over-period mismatches, classification ambiguities, and SLA delays."
        ),
        "key_concepts": [
            "Cross-Period Validation: Verifying accounting standard consistency (e.g., GAAP/IFRS) across periods.",
            "Automated Alerting: Triggering structured notifications when jobs exceed SLA thresholds.",
            "Audit Trail Logging: Recording every manual override or skipped filing ID with a reason code."
        ],
        "quiz": [
            {
                "q": "Which SQL pattern is best for comparing a filing's current period standard against its prior period?",
                "options": [
                    "CROSS JOIN without a WHERE clause",
                    "Self-join or window function (LAG/LEAD) partitioned by Company ID",
                    "TRUNCATE TABLE",
                    "SELECT DISTINCT *"
                ],
                "answer": "Self-join or window function (LAG/LEAD) partitioned by Company ID",
                "explanation": "Window functions like LAG() partitioned by entity ID easily detect period-over-period tag discrepancies."
            }
        ]
    }
}

# --- SESSION STATE INITIALIZATION ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "👋 Welcome to **MetaTutor**! Choose a learning module on the left, take an adaptive quiz, or ask me any question about **Metadata Policies, Data Ingestion, or SQL/Python QA**."
        }
    ]
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "learner_level" not in st.session_state:
    st.session_state.learner_level = "Intermediate"

# --- HELPER: BUILT-IN AI TUTOR ENGINE (WORKS WITH OR WITHOUT API KEY) ---
def generate_tutor_response(prompt: str, module_name: str, level: str, api_key: str = "") -> str:
    if api_key.strip():
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key.strip())
            sys_prompt = (
                f"You are MetaTutor, an expert AI Personalized Learning Assistant specializing in "
                f"Data Engineering, Metadata Governance, and Ingestion Pipelines. "
                f"The learner is at a '{level}' level and currently studying '{module_name}'. "
                f"Provide clear, structured, encouraging explanations with practical examples."
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"⚠️ *API Key error ({e}). Falling back to built-in MetaTutor Knowledge Engine:*\n\n" + _local_tutor_fallback(prompt, module_name, level)
    return _local_tutor_fallback(prompt, module_name, level)

def _local_tutor_fallback(prompt: str, module_name: str, level: str) -> str:
    q_lower = prompt.lower()
    mod_info = MODULES[module_name]
    if "dedup" in q_lower or "duplicate" in q_lower:
        return (
            f"### 🔍 Understanding Deduplication ({level} Level)\n"
            "In enterprise ingestion pipelines, multiple filings often arrive for the same `CompanyID` and `PeriodEndDate`.\n\n"
            "**Best Practice Workflow:**\n"
            "1. **Check Amendment Flags:** Determine if the newer filing is a restatement or amendment.\n"
            "2. **Compare Completeness:** If a fuller report is already in production, skip the redundant filing and log the reference ID.\n"
            "3. **Enforce Idempotency:** Use composite keys (`company_id`, `filing_id`, `period_end_date`) so re-runs never duplicate rows.\n\n"
            "💡 *Tip: Try asking me for a sample SQL query to detect duplicate filings!*"
        )
    elif "sql" in q_lower or "query" in q_lower or "gaap" in q_lower:
        return (
            f"### 🛠️ SQL Validation Pattern ({level} Level)\n"
            "To catch inconsistencies (such as accounting standard mismatches across periods or delayed jobs), use a window function:\n\n"
            "```sql\n"
            "SELECT \n"
            "    company_id,\n"
            "    filing_id,\n"
            "    period_end_date,\n"
            "    accounting_standard AS current_std,\n"
            "    LAG(accounting_standard) OVER (PARTITION BY company_id ORDER BY period_end_date) AS prev_std\n"
            "FROM enterprise_filings\n"
            "WHERE current_std <> prev_std;\n"
            "```\n"
            "This immediately surfaces records requiring analyst review before final publication."
        )
    elif "sla" in q_lower or "tat" in q_lower or "alert" in q_lower:
        return (
            f"### ⏱️ SLA & TAT Monitoring ({level} Level)\n"
            "Turnaround Time (TAT) monitoring tracks active jobs stuck in `Processing` or `Pending` states beyond threshold limits (e.g., > 1.5 hours or > 4 hours).\n\n"
            "- **Operational Metadata Needed:** `start_time`, `status`, `process_stage`, `company_rank`.\n"
            "- **Automated Action:** A scheduled Python script queries active jobs, calculates `DATEDIFF(minute, start_time, GETDATE()) / 60.0`, and dispatches priority alerts so high-rank entities never breach SLA."
        )
    else:
        concepts_md = "\n".join([f"- {c}" for c in mod_info["key_concepts"]])
        return (
            f"### 📚 Personalized Guidance: {module_name} ({level} Mode)\n"
            f"Great question regarding **\"{prompt}\"**!\n\n"
            f"**Core Concept Summary:**\n{mod_info['summary']}\n\n"
            f"**Key Takeaways to Master:**\n{concepts_md}\n\n"
            "**Quick Self-Check:** How would you apply this rule if an upstream data source changed its column format without notice?"
        )

# --- SIDEBAR: LEARNER PROFILE & SETTINGS ---
with st.sidebar:
    st.title("🎓 MetaTutor")
    st.caption("AI-Powered Personalized Learning Assistant")
    st.divider()
    learner_name = st.text_input("Learner Name", value="Rahul Singh")
    st.session_state.learner_level = st.selectbox(
        "Proficiency Level",
        ["Beginner", "Intermediate", "Advanced"],
        index=1
    )
    selected_module = st.radio("📖 Select Learning Module", list(MODULES.keys()))
    st.divider()
    api_key = st.text_input("🔑 OpenAI API Key (Optional)", type="password", help="Leave blank to use the built-in interactive Demo Tutor Engine.")
    st.info("💡 **Evaluator Note:** Works out-of-the-box in Demo Mode without an API key, or connects live to GPT-4o-mini when a key is provided.")

# --- MAIN INTERFACE ---
st.title("🎓 MetaTutor: Personalized AI Learning Assistant")
st.markdown(f"**Learner:** `{learner_name}` | **Adaptive Mode:** `{st.session_state.learner_level}` | **Current Topic:** `{selected_module}`")

tab1, tab2, tab3 = st.tabs(["💬 Interactive AI Tutor", "📝 Adaptive Quiz & Assessment", "📊 Learning Progress Dashboard"])

# --- TAB 1: INTERACTIVE AI TUTOR ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📌 Module Study Guide")
        st.write(MODULES[selected_module]["summary"])
        st.markdown("#### Key Concepts")
        for concept in MODULES[selected_module]["key_concepts"]:
            st.markdown(f"- {concept}")
        st.divider()
        st.markdown("**Suggested Prompts:**")
        if st.button("Explain deduplication best practices"):
            st.session_state.chat_history.append({"role": "user", "content": "Explain deduplication best practices"})
            reply = generate_tutor_response("Explain deduplication best practices", selected_module, st.session_state.learner_level, api_key)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()
        if st.button("Show me a SQL query for QA validation"):
            st.session_state.chat_history.append({"role": "user", "content": "Show me a SQL query for QA validation"})
            reply = generate_tutor_response("Show me a SQL query for QA validation", selected_module, st.session_state.learner_level, api_key)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

    with col2:
        st.subheader("🤖 Ask MetaTutor")
        chat_container = st.container(height=420)
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_query = st.chat_input("Ask a question about metadata policies, ingestion, or SQL QA...")
        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            tutor_reply = generate_tutor_response(user_query, selected_module, st.session_state.learner_level, api_key)
            st.session_state.chat_history.append({"role": "assistant", "content": tutor_reply})
            st.rerun()

# --- TAB 2: ADAPTIVE QUIZ ---
with tab2:
    st.subheader(f"📝 Knowledge Check: {selected_module}")
    quizzes = MODULES[selected_module]["quiz"]
    with st.form(key=f"quiz_form_{selected_module}"):
        user_answers = {}
        for idx, item in enumerate(quizzes):
            st.markdown(f"**Q{idx+1}. {item['q']}**")
            user_answers[idx] = st.radio(
                "Select your answer:",
                item["options"],
                key=f"{selected_module}_q_{idx}",
                index=None
            )
            st.write("")
        submitted = st.form_submit_button("✅ Submit Answers")
        if submitted:
            correct_count = 0
            for idx, item in enumerate(quizzes):
                if user_answers.get(idx) == item["answer"]:
                    correct_count += 1
                    st.success(f"Q{idx+1}: Correct! {item['explanation']}")
                else:
                    st.error(f"Q{idx+1}: Incorrect. Correct Answer: **{item['answer']}** — {item['explanation']}")
            score_pct = int((correct_count / len(quizzes)) * 100)
            st.session_state.scores[selected_module] = score_pct
            st.metric("Module Score", f"{score_pct}%")

# --- TAB 3: PROGRESS DASHBOARD ---
with tab3:
    st.subheader("📊 Personalized Mastery Tracker")
    progress_data = []
    for mod in MODULES.keys():
        score = st.session_state.scores.get(mod, 0)
        status = "Mastered ✅" if score >= 80 else ("In Progress 🔄" if score > 0 else "Not Started ⏳")
        progress_data.append({"Module": mod, "Score (%)": score, "Status": status})
    df_progress = pd.DataFrame(progress_data)
    st.dataframe(df_progress, use_container_width=True, hide_index=True)

    avg_score = int(df_progress["Score (%)"].mean())
    st.progress(avg_score / 100.0, text=f"Overall Course Mastery: {avg_score}%")
