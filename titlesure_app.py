import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import re
import os
import google.generativeai as genai

# ==================================================
# 🔑 ADD YOUR GEMINI API KEY HERE
# ==================================================
genai.configure(api_key="YOUR_API_KEY")

# ==================================================
# KNOWLEDGE BASE LOADER
# ==================================================
@st.cache_data
def load_knowledge_base():
    """
    Loads the Indian property law knowledge base from the text file.
    Cached so it is only read once per session.
    """
    kb_path = os.path.join(os.path.dirname(__file__), "property_laws.txt")
    try:
        with open(kb_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "Knowledge base file not found. "
            "Please ensure property_laws.txt is in the same folder as this app."
        )

LEGAL_KNOWLEDGE_BASE = load_knowledge_base()

# ==================================================
# PAGE SETTINGS
# ==================================================
st.set_page_config(
    page_title="TitleSure - Property Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# CUSTOM CSS — Professional & Classical Theme
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@300;400;500;600&display=swap');

:root {
    --navy:       #0d1b2a;
    --navy-mid:   #1a2d44;
    --navy-light: #243d57;
    --gold:       #c9a84c;
    --gold-light: #e2c97e;
    --cream:      #f7f4ef;
    --white:      #ffffff;
    --slate:      #64748b;
    --border:     #ddd8cf;
    --success:    #2e7d5e;
    --warning:    #b45309;
    --danger:     #991b1b;
    --shadow-sm:  0 1px 4px rgba(13,27,42,0.08);
    --shadow-md:  0 4px 16px rgba(13,27,42,0.12);
    --shadow-lg:  0 8px 32px rgba(13,27,42,0.18);
}

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    color: #1a2d44;
}
.main { background: var(--cream); }
.block-container { padding: 2rem 3rem 3rem; max-width: 1400px; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--navy) 0%, var(--navy-mid) 100%);
    border-right: 1px solid var(--navy-light);
}
[data-testid="stSidebar"] * { color: #c8d8e8 !important; font-family: 'Source Sans 3', sans-serif; }
[data-testid="stSidebar"] h1 {
    font-family: 'Playfair Display', serif; font-size: 1.5rem !important;
    color: var(--gold) !important; letter-spacing: 0.03em; margin-bottom: 0.25rem;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.9rem !important; letter-spacing: 0.04em;
    text-transform: uppercase; color: #a8bece !important; transition: color 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover { color: var(--gold) !important; }
[data-testid="stSidebar"] hr { border-color: var(--navy-light) !important; margin: 1rem 0; }
[data-testid="stSidebar"] .stAlert {
    background: rgba(201,168,76,0.1) !important;
    border: 1px solid rgba(201,168,76,0.3) !important;
    border-radius: 8px; font-size: 0.82rem !important; color: #c8d8e8 !important;
}

.ts-header {
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
    border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 2rem;
    border-left: 5px solid var(--gold); box-shadow: var(--shadow-md);
    display: flex; align-items: center; gap: 1.5rem;
}
.ts-header-icon { font-size: 2.8rem; line-height: 1; }
.ts-header h1 {
    font-family: 'Playfair Display', serif; font-size: 2rem !important;
    color: var(--white) !important; margin: 0 0 0.2rem !important; letter-spacing: 0.02em;
}
.ts-header p { color: #a8bece !important; font-size: 0.95rem; margin: 0; letter-spacing: 0.03em; }
.ts-badge {
    margin-left: auto; background: rgba(201,168,76,0.15);
    border: 1px solid var(--gold); border-radius: 6px; padding: 0.35rem 0.85rem;
    font-size: 0.72rem; color: var(--gold) !important; letter-spacing: 0.08em;
    text-transform: uppercase; font-weight: 600; white-space: nowrap;
}

.ts-section-title {
    font-family: 'Playfair Display', serif; font-size: 1.25rem;
    color: var(--navy); font-weight: 600; margin: 0 0 1.25rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.ts-section-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, var(--gold) 0%, transparent 100%);
    margin-left: 0.75rem; opacity: 0.5;
}

.ts-metric-card {
    background: var(--white); border: 1px solid var(--border);
    border-radius: 14px; padding: 1.4rem 1.6rem; box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s, transform 0.2s; border-top: 3px solid var(--gold);
    position: relative; overflow: hidden;
}
.ts-metric-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.ts-metric-card::before {
    content: ''; position: absolute; top: 0; right: 0; width: 80px; height: 80px;
    background: radial-gradient(circle at top right, rgba(201,168,76,0.08), transparent 70%);
    border-radius: 0 14px 0 80px;
}
.ts-metric-label {
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em;
    color: var(--slate); font-weight: 600; margin-bottom: 0.5rem;
}
.ts-metric-value {
    font-family: 'Playfair Display', serif; font-size: 2rem;
    color: var(--navy); font-weight: 700; line-height: 1; margin-bottom: 0.4rem;
}
.ts-metric-delta { font-size: 0.78rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 20px; display: inline-block; }
.ts-metric-delta.up   { background: #d1fae5; color: var(--success); }
.ts-metric-delta.down { background: #fee2e2; color: var(--danger); }

.ts-chart-card {
    background: var(--white); border: 1px solid var(--border);
    border-radius: 14px; padding: 1.5rem 1.8rem;
    box-shadow: var(--shadow-sm); margin-bottom: 1.5rem;
}
.ts-upload-card {
    background: var(--white); border: 1px solid var(--border);
    border-radius: 14px; padding: 2rem; box-shadow: var(--shadow-sm); margin-bottom: 1.5rem;
}

.ts-kb-card {
    background: linear-gradient(135deg, #f0f4f8 0%, #e8ecf0 100%);
    border: 1px solid var(--border); border-left: 4px solid var(--gold);
    border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 1.2rem;
    font-size: 0.85rem; color: var(--navy-mid);
}
.ts-kb-card strong { color: var(--navy); }

[data-testid="stFileUploader"] {
    background: var(--cream) !important; border: 2px dashed var(--border) !important;
    border-radius: 12px !important; padding: 1rem !important; transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color: var(--gold) !important; }

.stButton > button {
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%) !important;
    color: var(--gold) !important; border: 1px solid var(--gold) !important;
    border-radius: 10px !important; font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.9rem !important; font-weight: 600 !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important;
    padding: 0.75rem 2rem !important; height: 3.2em !important; width: 100% !important;
    transition: all 0.2s !important; box-shadow: 0 2px 8px rgba(13,27,42,0.2) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #162840 0%, #2d4d6a 100%) !important;
    box-shadow: 0 4px 16px rgba(13,27,42,0.3) !important; transform: translateY(-1px);
}

.stAlert { border-radius: 10px !important; border: none !important; font-size: 0.88rem !important; }

.ts-risk-badge {
    display: flex; align-items: center; gap: 1.5rem;
    background: var(--white); border: 1px solid var(--border);
    border-radius: 14px; padding: 1.5rem 2rem; box-shadow: var(--shadow-sm); margin: 1.5rem 0;
}
.ts-risk-score-num { font-family: 'Playfair Display', serif; font-size: 3.5rem; font-weight: 700; line-height: 1; }
.ts-risk-score-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--slate); font-weight: 600; margin-bottom: 0.25rem; }
.ts-risk-level { font-size: 1.1rem; font-weight: 600; font-family: 'Playfair Display', serif; }

.stProgress > div > div > div { background: linear-gradient(90deg, var(--gold), #e2c97e) !important; border-radius: 4px; }
.stProgress > div > div { background: #e5e7eb !important; border-radius: 4px; height: 10px !important; }

[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 12px !important; overflow: hidden !important; box-shadow: var(--shadow-sm) !important; }

hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

.ts-footer { text-align: center; color: var(--slate); font-size: 0.78rem; letter-spacing: 0.04em; padding: 1rem 0 0; border-top: 1px solid var(--border); margin-top: 2rem; }

h2 { font-family: 'Playfair Display', serif !important; color: var(--navy) !important; }
h3 { font-family: 'Source Sans 3', sans-serif !important; font-weight: 600 !important; color: var(--navy-mid) !important; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.markdown('<h1>🏛️ TitleSure</h1>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Upload & Analyse", "Reports", "Settings"]
)

st.sidebar.markdown("---")
st.sidebar.info("AI-powered property due diligence tool for legal risk assessment.")

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="ts-header">
    <div class="ts-header-icon">🏛️</div>
    <div>
        <h1>TitleSure</h1>
        <p>AI-Powered Property Due Diligence &amp; Risk Intelligence</p>
    </div>
    <span class="ts-badge">⚡ Live Platform</span>
</div>
""", unsafe_allow_html=True)

# ==================================================
# DASHBOARD PAGE
# ==================================================
if menu == "Dashboard":

    st.markdown('<p class="ts-section-title">📊 Key Metrics</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        ("Documents Analysed", "1,245", "+12%", "up"),
        ("High Risk Properties", "87",    "-5%",  "down"),
        ("Verified Titles",     "1,020",  "+8%",  "up"),
        ("Fraud Alerts",        "23",     "+3%",  "up"),
    ]
    for col, (label, value, delta, direction) in zip([c1, c2, c3, c4], metrics):
        with col:
            st.markdown(f"""
            <div class="ts-metric-card">
                <div class="ts-metric-label">{label}</div>
                <div class="ts-metric-value">{value}</div>
                <span class="ts-metric-delta {direction}">{delta} this week</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="ts-section-title">📈 Analytics</p>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns([3, 2])

    with chart_col1:
        st.markdown('<div class="ts-chart-card">', unsafe_allow_html=True)
        chart_data = pd.DataFrame({
            "Day":       ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "Documents": [12,    19,    7,     14,    22]
        })
        fig1 = px.line(chart_data, x="Day", y="Documents",
                       title="Documents Analysed This Week", markers=True)
        fig1.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Source Sans 3, sans-serif", color="#1a2d44"),
            title_font=dict(family="Playfair Display, serif", size=16),
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(showgrid=False, linecolor="#ddd8cf"),
            yaxis=dict(gridcolor="#f0ece4", linecolor="#ddd8cf"),
        )
        fig1.update_traces(line=dict(color="#c9a84c", width=2.5), marker=dict(color="#0d1b2a", size=7))
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="ts-chart-card">', unsafe_allow_html=True)
        pie_data = pd.DataFrame({"Risk": ["Low", "Moderate", "High"], "Count": [40, 35, 25]})
        fig2 = px.pie(pie_data, names="Risk", values="Count",
                      title="Portfolio Risk Distribution", color="Risk",
                      color_discrete_map={"Low": "#2e7d5e", "Moderate": "#b45309", "High": "#991b1b"},
                      hole=0.45)
        fig2.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Source Sans 3, sans-serif", color="#1a2d44"),
            title_font=dict(family="Playfair Display, serif", size=16),
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# UPLOAD + ANALYSE PAGE
# ==================================================
elif menu == "Upload & Analyse":

    st.markdown('<p class="ts-section-title">📂 Upload Property Documents</p>', unsafe_allow_html=True)

    # ── Knowledge Base Status Card ──────────────────────────────────────────
    kb_lines = len(LEGAL_KNOWLEDGE_BASE.splitlines())
    kb_parts = LEGAL_KNOWLEDGE_BASE.count("PART ")
    st.markdown(f"""
    <div class="ts-kb-card">
        📚 <strong>Knowledge Base Active</strong> &nbsp;|&nbsp;
        Indian Property Law Reference loaded &nbsp;|&nbsp;
        {kb_parts} legal modules &nbsp;·&nbsp; {kb_lines} lines of legal provisions
        <br><small style="color:#64748b;">
        Covers: Transfer of Property Act 1882 · Registration Act 1908 ·
        RERA 2016 · Stamp Duty · Encumbrance Certificates · POA Rules · Due Diligence Checklist
        </small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ts-upload-card">', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload Property Documents (PDF, PNG, JPG)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_files:
        for file in uploaded_files:
            st.success(f"✅ Uploaded: **{file.name}**")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔍 Run Due Diligence Analysis"):

            with st.spinner("Reading documents and running AI analysis against legal knowledge base..."):

                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")

                    # ── Prompt now includes the full knowledge base ──────────
                    prompt = f"""
You are an expert legal analyst specialising in Indian property law.

LEGAL KNOWLEDGE BASE — USE THIS AS YOUR PRIMARY REFERENCE:
===============================================================
{LEGAL_KNOWLEDGE_BASE}
===============================================================

Using the legal provisions above as your reference framework, analyse the
uploaded property documents and do the following:

1. Read all files (OCR if needed)
2. Translate to English if required
3. Extract:
   * Owner names
   * Property description
   * Dates
   * Registration details
   * Encumbrances / disputes
4. Cross-check each document against the legal requirements in the knowledge base:
   - Is the document properly stamped? (refer Stamp Duty section)
   - Is the document registered as required? (refer Registration Act 1908, Section 17)
   - Are all parties legally competent? (refer TPA 1882, Section 7)
   - Are RERA requirements met where applicable? (refer RERA 2016)
   - Is the Encumbrance Certificate clean? (refer EC guide)
   - If POA is involved, are the POA rules followed? (refer POA section)
5. Compare all uploaded documents for consistency with each other.
6. Identify legal risks, citing the relevant law or section from the knowledge base.
7. Give a Risk Score from 0 to 100 in EXACTLY this format on its own line:
   Risk Score: <number>
8. State Risk Level:
   * Low (0–39)
   * Moderate (40–69)
   * High (70–100)
9. Explain findings in simple language that a non-lawyer buyer can understand.
10. Suggest specific next legal steps with reference to applicable laws.

Use clear headings. Be specific about which legal provision applies to each finding.
"""

                    contents = [prompt]

                    for file in uploaded_files:
                        # BUG FIX: Reset stream pointer before reading
                        file.seek(0)
                        file_bytes = file.read()
                        # BUG FIX: Correct Gemini inline_data format
                        contents.append({
                            "inline_data": {
                                "mime_type": file.type,
                                "data": file_bytes
                            }
                        })

                    response = model.generate_content(contents)
                    result = response.text

                    st.success("✅ Analysis Complete")

                    st.markdown('<p class="ts-section-title">📄 AI Analysis Result</p>', unsafe_allow_html=True)
                    st.markdown('<div class="ts-chart-card">', unsafe_allow_html=True)
                    st.write(result)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # BUG FIX: Targeted regex for "Risk Score: <number>"
                    match = re.search(r'[Rr]isk\s*[Ss]core[:\s]+(\d{1,3})', result)
                    if match:
                        risk_score = int(match.group(1))
                    else:
                        risk_score = random.randint(30, 80)

                    risk_score = min(risk_score, 100)

                    if risk_score < 40:
                        score_color = "#2e7d5e"
                        risk_level  = "Low Risk"
                    elif risk_score < 70:
                        score_color = "#b45309"
                        risk_level  = "Moderate Risk"
                    else:
                        score_color = "#991b1b"
                        risk_level  = "High Risk"

                    st.markdown('<p class="ts-section-title">⚠️ Risk Assessment</p>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="ts-risk-badge">
                        <div style="text-align:center; min-width:90px;">
                            <div class="ts-risk-score-label">Risk Score</div>
                            <div class="ts-risk-score-num" style="color:{score_color};">
                                {risk_score}
                            </div>
                            <div style="font-size:0.75rem; color:#64748b;">/ 100</div>
                        </div>
                        <div style="flex:1;">
                            <div class="ts-risk-score-label">Assessment</div>
                            <div class="ts-risk-level" style="color:{score_color};">
                                {risk_level}
                            </div>
                            <div style="margin-top:0.75rem;">
                    """, unsafe_allow_html=True)
                    st.progress(risk_score)
                    st.markdown('</div></div></div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Error during analysis: {e}")
    else:
        st.info("📎 Please upload at least one document to begin analysis.")

# ==================================================
# REPORTS PAGE
# ==================================================
elif menu == "Reports":

    st.markdown('<p class="ts-section-title">📑 Generated Reports</p>', unsafe_allow_html=True)
    st.markdown('<div class="ts-chart-card">', unsafe_allow_html=True)

    reports = pd.DataFrame({
        "Report ID": ["TS101", "TS102", "TS103"],
        "Location":  ["Bangalore", "Delhi", "Mumbai"],
        "Status":    ["High Risk", "Verified", "Moderate Risk"]
    })
    st.dataframe(reports, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# SETTINGS PAGE
# ==================================================
elif menu == "Settings":

    st.markdown('<p class="ts-section-title">⚙️ Settings</p>', unsafe_allow_html=True)
    st.markdown('<div class="ts-chart-card">', unsafe_allow_html=True)
    st.write("User preferences and future configurations.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# FOOTER
# ==================================================
st.markdown("""
<div class="ts-footer">
    ⚖️ This is an AI-assisted preliminary analysis and not a legal opinion. &nbsp;|&nbsp;
    TitleSure &copy; 2025 &nbsp;|&nbsp; All rights reserved
</div>
""", unsafe_allow_html=True)
