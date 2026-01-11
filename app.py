import subprocess as sp
import streamlit as st
import pandas as pd
from database.db import init_db
from database.bank_crud import (
    create_account, get_account, list_accounts,
    add_faq, get_all_faqs, search_faqs, 
    get_faqs_by_category, update_faq, delete_faq
)
from database.security import verify_password
from dialogue_manager.dialogue_handler import DialogueHandler

# Session state init
if "handler" not in st.session_state:
    st.session_state.handler = DialogueHandler()
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

init_db()
st.set_page_config(page_title="BankBot", layout="wide")

# Enhanced Styling
st.markdown("""
<style>
/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2027, #203a43, #2c5364);
    color: white;
}
section[data-testid="stSidebar"] h1 { color: #ffffff; font-weight: 700; }
section[data-testid="stSidebar"] .stSelectbox > div { background-color: #ffffff; border-radius: 10px; padding: 4px; }
section[data-testid="stSidebar"] .stSelectbox label { color: #ffffff; font-weight: 600; }

/* Primary Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #1e88e5, #42a5f5) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}
button:not([kind="primary"]) {
    background: linear-gradient(135deg, #8e24aa, #ba68c8) !important;
    color: white !important;
    border-radius: 12px !important;
}

/* Admin Dashboard Card Styling */
.admin-header-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    margin-bottom: 40px;
    text-align: center;
}

.admin-main-title {
    color: #ffffff;
    font-size: 48px;
    font-weight: 900;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.admin-subtitle {
    color: #f0f0f0;
    font-size: 18px;
    font-weight: 400;
    margin-top: 0;
}

/* Navigation Card Styling */
.nav-card {
    background: white;
    padding: 30px 20px;
    border-radius: 16px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    cursor: pointer;
    text-align: center;
    height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border: 2px solid transparent;
}

.nav-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    border-color: currentColor;
}

.nav-card-icon {
    font-size: 48px;
    margin-bottom: 15px;
}

.nav-card-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #2c3e50;
}

.nav-card-desc {
    font-size: 13px;
    color: #7f8c8d;
    line-height: 1.4;
}

/* Color variations */
.card-queries { border-left: 5px solid #3498db; }
.card-queries:hover { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); }

.card-knowledge { border-left: 5px solid #2ecc71; }
.card-knowledge:hover { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }

.card-confidence { border-left: 5px solid #9b59b6; }
.card-confidence:hover { background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); }

.card-retrain { border-left: 5px solid #e67e22; }
.card-retrain:hover { background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); }

.card-logs { border-left: 5px solid #e91e63; }
.card-logs:hover { background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%); }

/* Metric Cards */
.dashboard-metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    text-align: center;
    border-left: 4px solid;
    margin-bottom: 20px;
}

.metric-label {
    font-size: 14px;
    color: #6c757d;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 42px;
    font-weight: 900;
    color: #2c3e50;
    margin: 0;
}

/* Section Headers */
.section-header-modern {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 20px 30px;
    border-radius: 12px;
    margin-bottom: 30px;
    border-left: 5px solid #3498db;
}

.section-header-modern h2 {
    color: #2c3e50;
    font-size: 28px;
    font-weight: 800;
    margin: 0;
}

/* Table Styling */
.dataframe {
    border-radius: 12px !important;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

/* Chart Container */
.chart-container {
    background: white;
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    margin: 20px 0;
}

/* FAQ Card Styling */
.faq-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 15px;
    border-left: 4px solid #3498db;
    transition: all 0.3s ease;
}

.faq-card:hover {
    box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    transform: translateX(5px);
}

/* Divider Styling */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(to right, transparent, #3498db, transparent);
    margin: 30px 0;
}

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
}

/* Input Field Enhancement */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 10px;
    border: 2px solid #e0e0e0;
    padding: 12px;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* Success/Warning/Error Box Enhancement */
.stSuccess, .stWarning, .stError, .stInfo {
    border-radius: 12px;
    padding: 15px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

def bottom_navigation(back_page=None, next_page=None):
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if next_page and st.button("➡ Next", key=f"next_{next_page}"):
            st.session_state.page = next_page
            st.rerun()
    with col3:
        if back_page and st.button("⬅ Back", key=f"back_{back_page}"):
            st.session_state.page = back_page
            st.rerun()

# Sidebar
st.sidebar.title("🏦 BankBot")
pages = ["🏠Home", "🧠User Query", "➕Create Account", "👤Login", "🤖Chatbot", "🗄️Database", "⏳History", "❓Help", "🛠️Admin Dashboard"]
if st.session_state.page not in pages:
    st.session_state.page = pages[0]
selected_page = st.sidebar.selectbox("📌 Navigate", pages, index=pages.index(st.session_state.page))
st.session_state.page = selected_page

# HOME
if st.session_state.page == "🏠Home":
    st.markdown("""
    <style>
    .home-container { background: linear-gradient(135deg, #eef2f3, #ffffff); padding: 50px; border-radius: 24px; }
    .home-title { color: #000000; font-size: 42px; font-weight: 900; margin-bottom: 12px; }
    .home-subtitle { color: #444; font-size: 18px; margin-bottom: 30px; }
    .feature-card { padding: 26px; border-radius: 18px; text-align: center; font-size: 16px; font-weight: 700; box-shadow: 0px 10px 25px rgba(0,0,0,0.08); transition: transform 0.2s ease-in-out; }
    .feature-card:hover { transform: translateY(-6px); }
    .create { background: #e3f2fd; color: #0d47a1; }
    .login { background: #e8f5e9; color: #1b5e20; }
    .balance { background: #fff8e1; color: #ff6f00; }
    .transfer { background: #f3e5f5; color: #4a148c; }
    .block { background: #fdecea; color: #b71c1c; }
    </style>
    <div class="home-container">
        <div class="home-title">🏦 AI Chatbot for Banking FAQs</div>
        <div class="home-subtitle">Your AI-powered banking assistant for secure, fast and smart banking</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("<div class='feature-card create'>➕<br>Create Account</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='feature-card login'>🔐<br>Secure Login</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='feature-card balance'>💰<br>Check Balance</div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='feature-card transfer'>🔄<br>Money Transfer</div>", unsafe_allow_html=True)
    with col5:
        st.markdown("<div class='feature-card block'>🚫<br>Card Blocking</div>", unsafe_allow_html=True)
    
    bottom_navigation(None, "🧠User Query")

# USER QUERY
elif st.session_state.page == "🧠User Query":
    st.title("🧠 User Query – NLU Engine (Milestone 1)")
    st.info("This will open the Milestone-1 NLU Intent Recognition & Entity Extraction UI.")
    if st.button("🚀 Open NLU Engine"):
        sp.Popen(["streamlit", "run", "milestone1_app.py"])
        st.success("Milestone-1 NLU UI launched in a new window/tab.")
    bottom_navigation("🏠Home", "➕Create Account")

# CREATE ACCOUNT
elif st.session_state.page == "➕Create Account":
    st.title("📝 Create Account")
    name = st.text_input("User Name")
    acc_no = st.text_input("Account Number")
    acc_type = st.selectbox("Account Type", ["Savings", "Current"])
    balance = st.number_input("Initial Balance", min_value=0)
    password = st.text_input("Set Password", type="password")
    if st.button("Create Account"):
        if not all([name, acc_no, password]):
            st.error("Please fill all fields")
        else:
            try:
                create_account(name, acc_no, acc_type, balance, password)
                st.success("✅ Account created successfully")
            except:
                st.error("⚠ Account already exists")
    bottom_navigation("🧠User Query", "👤Login")

# LOGIN SECTION 
elif st.session_state.page == "👤Login":
    st.title("🔐 User Login")
    if "forgot_mode" not in st.session_state:
        st.session_state.forgot_mode = False
    accounts = list_accounts()
    if not accounts:
        st.warning("⚠ No accounts available. Please create an account first.")
        bottom_navigation("➕Create Account", None)
    else:
        usernames = [acc[1] for acc in accounts]
        if not st.session_state.forgot_mode:
            username = st.selectbox("Select User Name", usernames)
            password = st.text_input("Password", type="password")
            col1, col2 = st.columns([6, 1])
            with col1:
                if st.button("Login"):
                    acc_no = None
                    for acc in accounts:
                        if acc[1] == username:
                            acc_no = acc[0]
                            break
                    account = get_account(acc_no)
                    if not verify_password(password, account[4]):
                        st.error("❌ Wrong password")
                    else:
                        st.success("✅ Login successful")
                        st.session_state.is_logged_in = True
                        st.session_state.logged_in_username = username
                        st.rerun()
            with col2:
                if st.button("Forgot Password?"):
                    st.session_state.forgot_mode = True
                    st.rerun()
        else:
            st.subheader("🔑 Update Password")
            username = st.selectbox("Select User Name", usernames)
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            if st.button("Update Password"):
                if not new_password or not confirm_password:
                    st.error("⚠ Please fill all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    acc_no = None
                    for acc in accounts:
                        if acc[1] == username:
                            acc_no = acc[0]
                            break
                    from database.bank_crud import update_password
                    update_password(acc_no, new_password)
                    st.success("✅ Password updated successfully")
                    st.session_state.forgot_mode = False
                    st.rerun()
            if st.button("⬅ Back to Login"):
                st.session_state.forgot_mode = False
                st.rerun()
        bottom_navigation("➕Create Account", "🤖Chatbot")

# CHATBOT SECTION 
elif st.session_state.page == "🤖Chatbot":
    st.title("🤖 BankBot – AI Banking Assistant")
    if not st.session_state.is_logged_in:
        st.warning("🔒 Please login to access the chatbot.")
        bottom_navigation("👤Login", None)
    else:
        if "logged_in_username" not in st.session_state:
            st.session_state.logged_in_username = "guest"
        
        st.markdown("""
        <style>
        .user-bubble { background-color: #DCF8C6; padding: 10px 14px; border-radius: 15px; margin: 8px 0; max-width: 70%; margin-left: auto; box-shadow: 0px 1px 3px rgba(0,0,0,0.1); }
        .bot-bubble { background-color: #F1F0F0; padding: 10px 14px; border-radius: 15px; margin: 8px 0; max-width: 70%; box-shadow: 0px 1px 3px rgba(0,0,0,0.1); }
        </style>
        """, unsafe_allow_html=True)
        
        for sender, msg in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f"<div class='user-bubble'>🧑 {msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bot-bubble'>🤖 {msg}</div>", unsafe_allow_html=True)
        
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Type your message...")
            send = st.form_submit_button("Send")
        
        if send and user_input.strip():
            st.session_state.handler.context["username"] = st.session_state.logged_in_username
            
            reply = st.session_state.handler.handle_message(user_input)
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("Bot", reply))
            st.rerun()
        
    bottom_navigation("👤Login", "🗄️Database")

# DATABASE
elif st.session_state.page == "🗄️Database":
    st.title("📊 Database Management")
    accounts = list_accounts()
    if accounts:
        df = pd.DataFrame(accounts, columns=["Account Number", "User Name"])
        st.table(df)
    else:
        st.info("No accounts found in database.")
    bottom_navigation("🤖Chatbot", "⏳History")

# HISTORY
elif st.session_state.page == "⏳History":
    st.title("🕒 Chat History")
    if not st.session_state.chat_history:
        st.info("No history found")
    else:
        for sender, msg in st.session_state.chat_history:
            st.write(f"{sender}: {msg}")
    bottom_navigation("🗄️Database", "❓Help")

# HELP
elif st.session_state.page == "❓Help":
    st.title("❓ Help & Support")
    st.markdown("### 📝 General Guidance")
    with st.expander("How to create an account?"):
        st.write("Go to the 'Create Account' page, fill in your details, set a secure password, and click 'Create Account'.")
    with st.expander("How to login?"):
        st.write("Go to the 'Login' page, enter your account number and password, then click 'Login'.")
    with st.expander("How to check balance and transaction history?"):
        st.write("After logging in, access the 'Chatbot' or 'Database' page to view your account details and transactions.")
    with st.expander("How to transfer money?"):
        st.write("Use the chatbot to request a money transfer. Example: 'Transfer ₹500 to account 12345'. Ensure you are logged in.")
    st.markdown("### 🔒 Security Tips")
    with st.expander("How to keep my account safe?"):
        st.write("Never share your password or PIN, avoid using public Wi-Fi, and do not click on suspicious links.")
    bottom_navigation("⏳History", "🛠️Admin Dashboard")

# ADMIN DASHBOARD 
elif st.session_state.page == "🛠️Admin Dashboard":
    
    # Admin Header
    st.markdown("""
    <div class="admin-header-container">
        <div class="admin-main-title">🛠️ Admin Control Panel</div>
        <div class="admin-subtitle">Comprehensive dashboard for system management, analytics, and AI model training</div>
    </div>
    """, unsafe_allow_html=True)
    
    import matplotlib.pyplot as plt
    from database.bank_crud import fetch_chat_history
    
    if st.button("🔄 Refresh Dashboard", type="primary"):
        st.rerun()
    
    chats = fetch_chat_history()
    df = pd.DataFrame(chats, columns=["ID", "User", "Query", "Intent", "Confidence", "Time"]) if chats else pd.DataFrame(columns=["ID", "User", "Query", "Intent", "Confidence", "Time"])
    
    # Filtering Function
    def is_initial_query(query, intent):
        query_lower = query.lower()
        
        if intent == "greet":
            greetings = ["hi", "hello", "hey", "good morning", "good evening", 
                        "thanks", "thank you", "thx", "thankyou"]
            return query_lower.strip() in greetings

        elif intent == "check_balance":
            balance_keywords = ["balance", "check", "account balance", "my balance", 
                               "saving", "current", "money", "funds"]
            has_keyword = any(keyword in query_lower for keyword in balance_keywords)
            is_just_number = query.strip().isdigit()
            is_password = len(query) < 20 and not any(c.isalpha() for c in query)
            
            return has_keyword and not is_just_number and not is_password
        
        elif intent == "transfer_money":
            transfer_keywords = ["transfer", "send", "pay", "money", "amount"]
            has_keyword = any(keyword in query_lower for keyword in transfer_keywords)
            is_just_number = query.strip().isdigit()
            
            return has_keyword and not is_just_number
        
        elif intent == "card_block":
            block_keywords = ["block", "card", "debit", "credit", "stolen", "lost", "fraud"]
            has_keyword = any(keyword in query_lower for keyword in block_keywords)
            is_just_reason = query_lower.strip() in ["lost", "stolen", "fraud"]
            
            return has_keyword and not is_just_reason
        
        elif intent == "llm":
            is_just_number = query.strip().isdigit()
            is_too_short = len(query.strip()) < 3
            
            return not is_just_number and not is_too_short
        
        return True
    
    if not df.empty:
        filtered_df = df[df.apply(lambda row: is_initial_query(row["Query"], row["Intent"]), axis=1)].copy()
    else:
        filtered_df = df.copy()
    
    # Navigation Cards 
    if "admin_view" not in st.session_state:
        st.session_state.admin_view = None
    
    st.markdown("### 📊 Dashboard Navigation")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="nav-card card-queries">
            <div class="nav-card-icon">📊</div>
            <div class="nav-card-title">Top Queries</div>
            <div class="nav-card-desc">View user query analytics and trends</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open", key="nav_queries", use_container_width=True):
            st.session_state.admin_view = None if st.session_state.admin_view == "queries" else "queries"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="nav-card card-knowledge">
            <div class="nav-card-icon">📚</div>
            <div class="nav-card-title">Knowledge Base</div>
            <div class="nav-card-desc">Manage FAQs and responses</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open", key="nav_knowledge", use_container_width=True):
            st.session_state.admin_view = None if st.session_state.admin_view == "knowledge_base" else "knowledge_base"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="nav-card card-confidence">
            <div class="nav-card-icon">📈</div>
            <div class="nav-card-title">Confidence</div>
            <div class="nav-card-desc">Monitor intent accuracy</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open", key="nav_confidence", use_container_width=True):
            st.session_state.admin_view = None if st.session_state.admin_view == "confidence" else "confidence"
            st.rerun()
    
    with col4:
        st.markdown("""
        <div class="nav-card card-retrain">
            <div class="nav-card-icon">🔁</div>
            <div class="nav-card-title">Model Training</div>
            <div class="nav-card-desc">Retrain NLU models</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open", key="nav_retrain", use_container_width=True):
            st.session_state.admin_view = None if st.session_state.admin_view == "retrain" else "retrain"
            st.rerun()
    
    with col5:
        st.markdown("""
        <div class="nav-card card-logs">
            <div class="nav-card-icon">💬</div>
            <div class="nav-card-title">Chat Logs</div>
            <div class="nav-card-desc">Review user interactions</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open", key="nav_logs", use_container_width=True):
            st.session_state.admin_view = None if st.session_state.admin_view == "logs" else "logs"
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # TOP QUERIES VIEW
    if st.session_state.admin_view == "queries":
        st.markdown('<div class="section-header-modern"><h2>📊 Top User Queries Analytics</h2></div>', unsafe_allow_html=True)
        
        if filtered_df.empty:
            st.warning("No data available")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="dashboard-metric-card" 
                    style="background: linear-gradient(135deg, #3498db 0%, #5dade2 100%);
                            border-left-color: #3498db;
                            color: white;">
                    <div class="metric-label" style="color:#eaf2f8;">Total Queries</div>
                    <div class="metric-value" style="color:white;">{len(filtered_df)}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="dashboard-metric-card" 
                    style="background: linear-gradient(135deg, #2ecc71 0%, #58d68d 100%);
                            border-left-color: #2ecc71;
                            color: white;">
                    <div class="metric-label" style="color:#eafaf1;">Unique Intents</div>
                    <div class="metric-value" style="color:white;">{filtered_df['Intent'].nunique()}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                avg_conf = filtered_df['Confidence'].mean() if not filtered_df.empty else 0
                st.markdown(f"""
                <div class="dashboard-metric-card" 
                    style="background: linear-gradient(135deg, #9b59b6 0%, #af7ac5 100%);
                            border-left-color: #9b59b6;
                            color: white;">
                    <div class="metric-label" style="color:#f5eef8;">Avg Confidence</div>
                    <div class="metric-value" style="color:white;">{avg_conf:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
           
            st.markdown("---")
            st.subheader("📋 Intent Distribution Table")
            st.markdown("""
            <style>
            /* ===== Intent Distribution Table (Sky Blue + Visible Text) ===== */

            /* Table background */
            div[data-testid="stDataFrame"] table,
            div[data-testid="stDataFrame"] tbody,
            div[data-testid="stDataFrame"] tr,
            div[data-testid="stDataFrame"] td {
                background-color: #e6f2ff !important;
            }

            /* Header */
            div[data-testid="stDataFrame"] th {
                background-color: #cfe8ff !important;
                color: #0f172a !important;
                font-weight: 600 !important;
            }

            /* Text inside cells */
            div[data-testid="stDataFrame"] td * {
                color: #0f172a !important;
                font-weight: 500 !important;
            }

            /* Index column */
            div[data-testid="stDataFrame"] th div,
            div[data-testid="stDataFrame"] td div {
                color: #0f172a !important;
            }
            </style>
            """, unsafe_allow_html=True)



            intent_df = filtered_df.groupby("Intent")["Query"].agg(Count='count').reset_index()
            intent_df.columns = ["Intent", "Count"]
            intent_df = intent_df.sort_values("Count", ascending=False)
            intent_df.reset_index(drop=True, inplace=True)
            intent_df.index = intent_df.index + 1
            st.dataframe(intent_df, use_container_width=True, height=300)
            
            st.markdown("---")
            st.subheader("📊 Visual Intent Analysis")
            color_map = {
                "greet": "#FF6B6B", 
                "check_balance": "#4ECDC4", 
                "transfer_money": "#45B7D1", 
                "card_block": "#FFA07A", 
                "llm": "#95E1D3"
            }
            intent_counts = filtered_df["Intent"].value_counts()
            colors = [color_map.get(intent, "#CCCCCC") for intent in intent_counts.index]
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.bar(intent_counts.index, intent_counts.values, color=colors, edgecolor='white', linewidth=2)
            ax.set_xlabel("Intent", fontsize=14, fontweight='bold', color='#2c3e50')
            ax.set_ylabel("Query Count", fontsize=14, fontweight='bold', color='#2c3e50')
            ax.set_title("Query Distribution by Intent", fontsize=16, fontweight='bold', color='#2c3e50', pad=20)
            ax.tick_params(axis='x', rotation=45, labelsize=11)
            ax.tick_params(axis='y', labelsize=11)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, 
                       f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=12)
            plt.tight_layout()
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            with st.expander("📝 View All Query Details", expanded=False):
                display_df = filtered_df[["Query", "Intent", "Confidence", "Time"]].sort_values("Time", ascending=False)
                display_df.reset_index(drop=True, inplace=True)
                display_df.index = display_df.index + 1
                st.dataframe(display_df, use_container_width=True, height=400)
    
    # KNOWLEDGE BASE VIEW
    elif st.session_state.admin_view == "knowledge_base":
        st.markdown('<div class="section-header-modern"><h2>📚 Knowledge Base Management</h2></div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📖 View All FAQs", "➕ Add New FAQ", "🔍 Search FAQs", "📊 By Category"])
        
        with tab1:
            st.markdown("### 📋 All FAQs in System")
            faqs = get_all_faqs()
            if not faqs:
                st.info("💡 No FAQs found. Add your first FAQ to get started!")
            else:
                st.markdown(f"""
                <div class="dashboard-metric-card" style="border-left-color: #2ecc71;">
                    <div class="metric-label">Total FAQs in Database</div>
                    <div class="metric-value">{len(faqs)}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("---")
                for faq in faqs:
                    faq_id, question, answer, category, created_at = faq
                    with st.expander(f"❓ {question}"):
                        st.markdown(f"**Category:** `{category}`")
                        st.markdown(f"**Answer:**")
                        st.info(answer)
                        st.caption(f"📅 Added on: {created_at}")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button(f"✏️ Edit", key=f"edit_{faq_id}"):
                                st.session_state.edit_faq_id = faq_id
                                st.session_state.edit_question = question
                                st.session_state.edit_answer = answer
                                st.session_state.edit_category = category
                                st.session_state.admin_view = "edit_faq"
                                st.rerun()
                        with col2:
                            if st.button(f"🗑️ Delete", key=f"delete_{faq_id}"):
                                delete_faq(faq_id)
                                st.success("FAQ deleted successfully!")
                                st.rerun()
        
        with tab2:
            st.markdown("### ➕ Add New FAQ to Knowledge Base")
            categories = ["greet", "check_balance", "transfer_money", "card_block", "account_info", "general"]
            new_question = st.text_area("Question", placeholder="e.g., How do I check my account balance?")
            new_answer = st.text_area("Answer", placeholder="You can check your balance by...", height=150)
            new_category = st.selectbox("Category", categories)
            if st.button("➕ Add FAQ", type="primary"):
                if new_question.strip() and new_answer.strip():
                    add_faq(new_question.strip(), new_answer.strip(), new_category)
                    st.success("✅ FAQ added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in both question and answer")
        
        with tab3:
            st.markdown("### 🔍 Search FAQs")
            search_term = st.text_input("Search by question or category", placeholder="Type to search...")
            if search_term:
                search_results = search_faqs(search_term)
                if not search_results:
                    st.warning(f"No results found for '{search_term}'")
                else:
                    st.success(f"Found {len(search_results)} result(s)")
                    st.markdown("---")
                    for faq in search_results:
                        faq_id, question, answer, category, created_at = faq
                        with st.expander(f"❓ {question}"):
                            st.markdown(f"**Category:** `{category}`")
                            st.markdown(f"**Answer:**")
                            st.info(answer)
                            st.caption(f"📅 Added on: {created_at}")
        
        with tab4:
            st.markdown("### 📊 FAQs by Category")
            categories = ["greetings", "check_balance", "transfer_money", "card_block", "account_info", "general"]
            selected_category = st.selectbox("Select Category", categories)
            if selected_category:
                category_faqs = get_faqs_by_category(selected_category)
                if not category_faqs:
                    st.info(f"No FAQs found in '{selected_category}' category")
                else:
                    st.success(f"Found {len(category_faqs)} FAQ(s) in '{selected_category}'")
                    st.markdown("---")
                    for faq in category_faqs:
                        faq_id, question, answer, category, created_at = faq
                        with st.expander(f"❓ {question}"):
                            st.markdown(f"**Answer:**")
                            st.info(answer)
                            st.caption(f"📅 Added on: {created_at}")
    
    # EDIT FAQ VIEW
    elif st.session_state.admin_view == "edit_faq":
        st.markdown('<div class="section-header-modern"><h2>✏️ Edit FAQ</h2></div>', unsafe_allow_html=True)
        
        categories = ["greetings", "check_balance", "transfer_money", "card_block", "account_info", "general"]
        edit_question = st.text_area("Question", value=st.session_state.edit_question)
        edit_answer = st.text_area("Answer", value=st.session_state.edit_answer, height=150)
        edit_category = st.selectbox("Category", categories, index=categories.index(st.session_state.edit_category))
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💾 Save Changes", type="primary"):
                if edit_question.strip() and edit_answer.strip():
                    update_faq(st.session_state.edit_faq_id, edit_question.strip(), edit_answer.strip(), edit_category)
                    st.success("✅ FAQ updated successfully!")
                    st.session_state.admin_view = "knowledge_base"
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in both question and answer")
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.admin_view = "knowledge_base"
                st.rerun()
    
    # CONFIDENCE VIEW
    elif st.session_state.admin_view == "confidence":
        st.markdown('<div class="section-header-modern"><h2>📈 Intent Confidence Analytics</h2></div>', unsafe_allow_html=True)
        
        if filtered_df.empty:
            st.warning("No data available")
        else:
            intent_counts = filtered_df["Intent"].value_counts()
            total_queries = intent_counts.sum()
            confidence_values = intent_counts / total_queries
            
            st.markdown("### 📊 Intent-wise Confidence Scores")
            st.markdown("<br>", unsafe_allow_html=True)
            
            color_map = {
                "greet": "#FF6B6B",
                "check_balance": "#4ECDC4", 
                "transfer_money": "#45B7D1",
                "card_block": "#FFA07A",
                "llm": "#95E1D3"
            }
            
            num_intents = len(intent_counts)
            cols = st.columns(num_intents)
            
            for idx, (intent, conf) in enumerate(confidence_values.items()):
                with cols[idx]:
                    color = color_map.get(intent, "#CCCCCC")
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
                                padding: 30px 15px; 
                                border-radius: 16px; 
                                text-align: center; 
                                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                                height: 180px;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                                transition: transform 0.3s ease;'>
                        <h4 style='color: white; margin: 0 0 15px 0; font-size: 15px; font-weight: 700; text-transform: uppercase;'>
                            {intent.replace('_', ' ').title()}
                        </h4>
                        <h1 style='color: white; margin: 10px 0; font-size: 48px; font-weight: 900;'>
                            {conf:.2f}
                        </h1>
                        <p style='color: rgba(255,255,255,0.9); margin: 0; font-size: 13px; font-weight: 600;'>
                            {intent_counts[intent]} queries
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### 🍩 Confidence Distribution Chart")
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            fig, ax = plt.subplots(figsize=(10, 10))
            colors = [color_map.get(intent, "#CCCCCC") for intent in intent_counts.index]
            
            wedges, texts, autotexts = ax.pie(
                confidence_values,
                labels=[intent.replace('_', ' ').title() for intent in intent_counts.index],
                autopct=lambda p: f"{p/100:.2f}",
                startangle=90,
                colors=colors,
                wedgeprops=dict(width=0.4, edgecolor='white', linewidth=3),
                textprops={'fontsize': 12, 'weight': 'bold'},
                pctdistance=0.75
            )
            
            for text in texts:
                text.set_color('#2c3e50')
                text.set_fontsize(13)
                text.set_weight('bold')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(14)
                autotext.set_weight('bold')
            
            ax.set_title("Intent Confidence Distribution", 
                        fontsize=18, fontweight='bold', color='#2c3e50', pad=20)
            ax.axis("equal")
            st.pyplot(fig)
            plt.close()
            st.markdown('</div>', unsafe_allow_html=True)
    
    # MODEL RETRAINING VIEW
    elif st.session_state.admin_view == "retrain":
        st.markdown('<div class="section-header-modern"><h2>🔁 NLU Model Retraining System</h2></div>', unsafe_allow_html=True)
        
        from nlu_engine.train_intent import load_intents, save_intents, retrain_nlu_model
        from nlu_engine.entity_extractor import EntityExtractor
        
        if "retrain_done" not in st.session_state:
            st.session_state.retrain_done = False
        
        intents_data = load_intents()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📚 Training Data", "➕ Add Example", "🆕 New Intent", "🔄 Train & Test"])
        
        with tab1:
            st.markdown("### 📊 Current Training Data Overview")
            total_examples = sum(len(examples) for examples in intents_data.values())
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="dashboard-metric-card" style="border-left-color: #3498db;">
                    <div class="metric-label">Total Intents</div>
                    <div class="metric-value">{len(intents_data)}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="dashboard-metric-card" style="border-left-color: #2ecc71;">
                    <div class="metric-label">Total Examples</div>
                    <div class="metric-value">{total_examples}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            for intent_name, examples in intents_data.items():
                with st.expander(f"🎯 {intent_name.replace('_', ' ').title()} ({len(examples)} examples)", expanded=False):
                    st.markdown(f"**Intent:** `{intent_name}`")
                    st.markdown(f"**Number of Examples:** {len(examples)}")
                    st.markdown("**Training Examples:**")
                    
                    for idx, example in enumerate(examples, 1):
                        st.markdown(f"{idx}. {example}")
                    
                    st.divider()
                    st.caption(f"💡 This intent has {len(examples)} training examples")
        
        with tab2:
            st.markdown("### ➕ Add New Training Example")
            st.info("📝 Add new examples to improve the NLU model's accuracy")
            
            if not intents_data:
                st.warning("⚠️ No intents found. Please create an intent first")
            else:
                intent_name = st.selectbox("Select Intent", list(intents_data.keys()), key="add_intent_select")
                
                current_count = len(intents_data[intent_name])
                st.markdown(f"""
                <div class="dashboard-metric-card" style="border-left-color: #9b59b6;">
                    <div class="metric-label">Current Examples for '{intent_name}'</div>
                    <div class="metric-value">{current_count}</div>
                </div>
                """, unsafe_allow_html=True)
                
                new_example = st.text_input(
                    "Add Training Example", 
                    placeholder=f"e.g., for 'greet': Hello there!",
                    key="add_example_input"
                )
                
                if new_example.strip():
                    st.markdown("**Preview:**")
                    st.success(f"Intent: `{intent_name}` → Example: \"{new_example}\"")
                
                if st.button("➕ Add Example", type="primary", key="add_example_btn"):
                    if new_example.strip():
                        intents_data[intent_name].append(new_example.strip())
                        save_intents(intents_data)
                        
                        st.success(f"✅ Example added to '{intent_name}' successfully!")
                        st.info(f"New example count: {len(intents_data[intent_name])}")
                        st.warning("⚠️ Please retrain the model to use this new example")
                        
                        st.session_state.retrain_done = False
                        st.rerun()
                    else:
                        st.warning("⚠ Please enter a valid example")
        
        with tab3:
            st.markdown("### 🆕 Create New Intent")
            st.info("🎯 Create a completely new intent with training examples")
            
            new_intent_name = st.text_input(
                "Intent Name",
                placeholder="e.g., loan_inquiry",
                key="new_intent_name"
            )
            
            new_intent_examples = st.text_area(
                "Training Examples (one per line)",
                placeholder="I want to apply for a loan\nHow can I get a personal loan?\nTell me about loan options",
                height=200,
                key="new_intent_examples"
            )
            
            if new_intent_name.strip() and new_intent_examples.strip():
                st.markdown("**Preview:**")
                intent_clean = new_intent_name.strip().lower().replace(" ", "_")
                example_lines = [line.strip() for line in new_intent_examples.split("\n") if line.strip()]
                st.info(f"Intent: `{intent_clean}` with {len(example_lines)} examples")
            
            if st.button("🆕 Create Intent", type="primary", key="create_intent_btn"):
                if new_intent_name.strip() and new_intent_examples.strip():
                    intent_clean = new_intent_name.strip().lower().replace(" ", "_")
                    
                    if intent_clean in intents_data:
                        st.error(f"⚠️ Intent '{intent_clean}' already exists!")
                    else:
                        examples = [line.strip() for line in new_intent_examples.split("\n") if line.strip()]
                        
                        if examples:
                            intents_data[intent_clean] = examples
                            save_intents(intents_data)
                            
                            st.success(f"✅ Intent '{intent_clean}' created with {len(examples)} examples!")
                            st.warning("⚠️ Please retrain the model to use this new intent")
                            
                            st.session_state.retrain_done = False
                            st.rerun()
                        else:
                            st.error("⚠️ Please provide at least one example")
                else:
                    st.warning("⚠️ Please fill in both intent name and examples")
        
        with tab4:
            st.markdown("### 🔄 Model Retraining")
            
            intents_data = load_intents()
            
            if not intents_data:
                st.warning("⚠️ No training data available")
            else:
                total_examples = sum(len(examples) for examples in intents_data.values())
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="dashboard-metric-card" style="border-left-color: #e67e22;">
                        <div class="metric-label">Training Data Status</div>
                        <div class="metric-value" style="font-size: 20px;">{len(intents_data)} intents | {total_examples} examples</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.retrain_done:
                        st.success("✅ Model is trained with latest data!")
                    else:
                        st.warning("⚠️ Model needs retraining")
                
                with col2:
                    if st.button("🔁 Train Model", type="primary", key="retrain_model_btn", use_container_width=True):
                        with st.spinner("Training model..."):
                            try:
                                success = retrain_nlu_model(intents_data)
                                if success:
                                    st.success("✅ Model retrained successfully!")
                                    st.balloons()
                                    st.session_state.retrain_done = True
                                    st.rerun()
                                else:
                                    st.error("❌ Model retraining failed!")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
            
            st.markdown("---")
            
            st.markdown("### 🧪 NLU Testing - Intent & Entity")
            st.info("🔍 Test intent recognition and entity extraction")
            
            test_query = st.text_area(
                "Enter a test query:",
                placeholder="e.g., Transfer 5000 to account 123456789",
                height=80,
                key="nlu_test_query"
            )
            
            if st.button("🔍 Analyze Query", type="primary", key="analyze_query_btn"):
                if test_query.strip():
                    try:
                        from nlu_engine.train_intent import classify_intent
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 🎯 Intent Recognition")
                            
                            intent_result = classify_intent(test_query)
                            predicted_intent = intent_result.get('intent', 'unknown')
                            confidence = intent_result.get('confidence', 0.0)
                            all_intents = intent_result.get('all_intents', {})
                            
                            st.metric("Predicted Intent", predicted_intent.replace('_', ' ').title())
                            st.metric("Confidence", f"{confidence:.2f}")
                            
                            confidence_color = "#4CAF50" if confidence > 0.70 else "#FF9800" if confidence > 0.50 else "#F44336"
                            st.markdown(f"""
                            <div style='background-color: #f0f0f0; border-radius: 10px; height: 30px; position: relative; overflow: hidden; margin-bottom: 15px;'>
                                <div style='background-color: {confidence_color}; width: {confidence*100}%; height: 100%; border-radius: 10px;'></div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if all_intents:
                                st.markdown("**All Intent Scores:**")
                                for intent_name, score in sorted(all_intents.items(), key=lambda x: x[1], reverse=True):
                                    if score > 0:
                                        st.markdown(
                                            f"""
                                            <div style='display:flex; justify-content:space-between; 
                                                        align-items:center;
                                                        padding:8px 12px; background:#f5f5f5; 
                                                        border-radius:8px; margin-bottom:5px;
                                                        border-left:3px solid #1f77ff;'>
                                                <span style='font-size:14px; font-weight:500;'>{intent_name.replace('_', ' ').title()}</span>
                                                <span style='font-size:14px; font-weight:600; color:#1f77ff;'>{score:.2f}</span>
                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )
                        
                        with col2:
                            st.markdown("#### 🏷️ Entity Extraction")
                            
                            extractor = EntityExtractor()
                            entities = extractor.extract(test_query)
                            
                            if entities:
                                st.success(f"✅ Found {len(entities)} entities")
                                for ent in entities:
                                    st.markdown(
                                        f"""
                                        <div style='display:flex; justify-content:space-between; 
                                                    align-items:center;
                                                    padding:10px 12px; background:#f9f9f9; 
                                                    border-radius:8px; margin-bottom:6px;
                                                    border-left:3px solid #28a745;'>
                                            <span style='font-size:14px; font-weight:600; color:#28a745;'>{ent['entity']}</span>
                                            <span style='font-size:14px; color:#333; background:#e8f5e9; 
                                                        padding:3px 10px; border-radius:6px;'>{ent['value']}</span>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                            else:
                                st.info("ℹ️ No entities found")
                        
                        st.markdown("---")
                        st.markdown("#### 💡 Analysis Summary")
                        summary = f"The model identified this as a **{predicted_intent.replace('_', ' ')}** query with **{confidence:.2f}** confidence. "
                        if entities:
                            entity_str = ", ".join([f"{e['entity']}={e['value']}" for e in entities])
                            summary += f"Extracted entities: {entity_str}"
                        else:
                            summary += "No entities detected."
                        st.success(summary)
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
                else:
                    st.warning("⚠️ Please enter a query to test")
    
    # USER CHAT LOGS VIEW
    elif st.session_state.admin_view == "logs":
        st.markdown('<div class="section-header-modern"><h2>💬 User Chat Logs</h2></div>', unsafe_allow_html=True)
        
        if filtered_df.empty:
            st.warning("No chat logs available")
        else:
            df_sorted = filtered_df.sort_values("Time", ascending=False).reset_index(drop=True)
            df_sorted.index = df_sorted.index + 1
            
            st.markdown(f"""
            <div class="dashboard-metric-card" style="border-left-color: #e91e63;">
                <div class="metric-label">Total Chat Interactions</div>
                <div class="metric-value">{len(df_sorted)}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.dataframe(df_sorted[["User", "Query", "Intent", "Confidence", "Time"]], use_container_width=True, height=500)
            
            st.markdown("---")
            
            with st.expander("⬇ Export Chat Logs"):
                csv = df_sorted.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇ Export as CSV",
                    csv,
                    "chat_history_filtered.csv",
                    "text/csv",
                    type="primary"
                )
    
    bottom_navigation("❓Help", None)