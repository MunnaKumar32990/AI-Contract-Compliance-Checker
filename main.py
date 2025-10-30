import streamlit as st
import agreement_comparision
import data_extraction
import json
import schedule
import time
import scrapping
import threading
import notifications as notification

# Set the page configuration for a modern, wide-screen look
st.set_page_config(
    page_title="AI Contract Compliance Checker",
    layout="wide",
    initial_sidebar_state="auto",
)

# --- Theme and Styling (Custom CSS for a modern look and result visualization) ---
st.markdown(
    """
    <style>
    /* General app styling */
    .stApp {
        background-color: #f0f2f6; /* Light gray background for contrast */
        color: #1c1e21; /* Dark text */
    }
    /* Style for the main upload button area (can be hidden if using a custom button) */
    .stFileUploader {
        border: 2px dashed #007BFF; /* Blue dashed border for the upload zone */
        padding: 20px;
        border-radius: 10px;
        background-color: #ffffff;
    }
    
    /* Risk Score Card Styling */
    .risk-score-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 30px;
        border-radius: 15px;
        background-color: #ffffff;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15); /* More prominent shadow */
        margin-bottom: 20px;
    }
    .risk-score-value {
        font-size: 5em; /* Larger font for the score */
        font-weight: 800;
        margin-bottom: 0.1em;
        line-height: 1.0;
    }
    .metric-label {
        font-size: 1.3em;
        color: #555555;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    /* Color coding for risk score based on value (Crucial UX feedback) */
    .risk-low { color: #28a745; }    /* Darker Green */
    .risk-medium { color: #ffc107; } /* Amber/Yellow */
    .risk-high { color: #dc3545; }   /* Darker Red */
    
    /* Styling for the st.info/st.success/st.error alerts for better contrast */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def run_scheduler():
    schedule.every().day.at("00:00").do(scrapping.call_scrape_function)
    # schedule.every(10).seconds.do(scrapping.call_scrape_function)  # run every 10s for testing

    while True:
        schedule.run_pending()
        time.sleep(1)


threading.Thread(target=run_scheduler, daemon=True).start()

def display_comparison_result(result_text):
    """
    Parses the structured result text from the model and displays it
    using Streamlit components for better visual appeal and structure.
    """
    
    # Simple regex-like parsing based on the expected format
    sections = {}
    current_key = None
    
    # Define keys based on your prompt structure
    KEYS = {
        '- Missing Clauses:': 'Missing Clauses',
        '- Potential Compliance Risks:': 'Potential Compliance Risks',
        '- Risk Score (0-100):': 'Risk Score',
        '- Reasoning:': 'Reasoning',
        '- Recommendations:': 'Recommendations'
    }
    
    lines = result_text.split('\n')
    for line in lines:
        matched = False
        for prefix, key in KEYS.items():
            if line.strip().startswith(prefix):
                current_key = key
                sections[current_key] = line.strip().replace(prefix, '').strip()
                matched = True
                break
        
        # If it's a continuation line and we have a current key
        if not matched and current_key and line.strip():
            sections[current_key] += '\n' + line.strip()

    
    # --- UI Layout for Results ---
    
    st.subheader("📊 Compliance Analysis Report")
    st.markdown("---")

    # 1. Risk Score Display (The most important metric first)
    risk_score = sections.get('Risk Score', 'N/A')
    score_value = 'N/A'
    
    if isinstance(risk_score, str):
        try:
            # Extract the numerical part
            score_str = risk_score.split(' ')[0].strip()
            score_value = int(score_str)
        except:
            pass # Keep score_value as 'N/A'

    
    if isinstance(score_value, int):
        # Determine color and emoji based on risk level
        if score_value <= 33:
            color_class = "risk-low"
            emoji = "✅ Low Risk"
        elif score_value <= 66:
            color_class = "risk-medium"
            emoji = "⚠️ Medium Risk"
        else:
            color_class = "risk-high"
            emoji = "🚨 High Risk"

        st.markdown(
            f"""
            <div class="risk-score-container">
                <div class="metric-label">OVERALL RISK LEVEL: {emoji}</div>
                <div class="risk-score-value {color_class}">{score_value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error(f"⚠️ Could not parse a numerical risk score from the AI output.")


    # 2. Key Sections Display (Using st.tabs for clean separation and focus)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚨 Potential Compliance Risks",
        "⚖️ Recommendations",
        "🧐 Missing Clauses",
        "💡 Reasoning"
    ])

    with tab1:
        st.header("Potential Compliance Risks")
        # Use st.error or st.warning for risks for emphasis
        risk_content = sections.get('Potential Compliance Risks', 'No specific compliance risks flagged.')
        if risk_content.lower().startswith('no'):
             st.info(risk_content)
        else:
             st.warning(risk_content)
    
    with tab2:
        st.header("Suggested Amendments/Recommendations")
        # Use st.success for action items/solutions
        st.success(sections.get('Recommendations', 'No immediate amendments suggested.'))
    
    with tab3:
        st.header("Missing or Altered Clauses")
        # Use st.code or st.markdown with bolding for clause details
        st.markdown("**Details on divergence from the template standard:**")
        st.code(sections.get('Missing Clauses', 'No critical clauses appear to be missing.'), language='markdown')

    with tab4:
        st.header("Reasoning for Risk Score")
        # Standard st.write is fine for reasoning
        st.write(sections.get('Reasoning', 'N/A'))


# ******** Phase 3 (Main Streamlit App Flow) ******** #
if __name__ == "__main__":
    try:
        # Mapping of agreement type to respective JSON file
        AGREEMENT_JSON_MAP = {
            "Data Processing Agreement": "json_files/dpa.json",
            "Joint Controller Agreement": "json_files/jca.json",
            "Controller-to-Controller Agreement": "json_files/c2c.json",
            "Processor-to-Subprocessor Agreement": "json_files/subprocessor.json",
            "Standard Contractual Clauses": "json_files/scc.json"
        }

        # --- Title and Header ---
        st.title("⚖️ AI Regulatory Compliance Checker")
        st.caption("Automated review of contractual agreements against regulatory templates (e.g., GDPR).")
        
        st.markdown("---")

        # --- File Upload Section (Using columns for a cleaner, centered look) ---
        col1, col_upload, col2 = st.columns([1, 4, 1])

        with col_upload:
            uploaded_file = st.file_uploader(
                "Upload a Contractual Agreement (PDF only)",
                type=["pdf"],
                help="Upload the document you need to check for compliance. The AI will handle the rest."
            )

        st.markdown("---")

        if uploaded_file is not None:
            # Save uploaded file temporarily
            with open("temp_uploaded.pdf", "wb") as f:
                f.write(uploaded_file.read())
            
            # Use a prominent spinner for visual engagement during processing
            with st.spinner("🧠 Step 1: Analyzing document type, extracting clauses, and running compliance comparison..."):
                
                # Step 1: Identify the type of agreement
                agreement_type = agreement_comparision.document_type("temp_uploaded.pdf")
                
                st.subheader("Document Identification")
                # Use st.metric for the detected type
                st.metric(label="Detected Document Type", value=agreement_type, delta="Compliance Scope Confirmed", delta_color="normal")
                
                # Check if the document type is supported/mapped
                if agreement_type in AGREEMENT_JSON_MAP:
                    
                    # Step 2: Extract clause data (functionality maintained)
                    unseen_data = data_extraction.Clause_extraction("temp_uploaded.pdf")
                    
                    # Step 3: Fetch stored template data (functionality maintained)
                    template_file = AGREEMENT_JSON_MAP[agreement_type]
                    with open(template_file, "r", encoding="utf-8") as f:
                        template_data = json.load(f)

                    # Step 4: Compare the unseen data with template data (functionality maintained)
                    result = agreement_comparision.compare_agreements(unseen_data, template_data)
                    
            # --- Show Detailed Results Outside the Spinner ---
            st.success("Analysis Complete! Review the compliance report below.")
            display_comparison_result(result)
            
            # Send notification (Now sends results via EMAIL)
            body = f"Agreement type is {agreement_type} \n Comparison Result: {result}"
            # *** UPDATED LINE ***
            notification.send_notification("Agreement Comparison Result (UI Generated)", body, notification_type="result") 
            

        else:
            # Clearer guidance for the user when no file is uploaded
            st.info("⬆️ Upload a PDF agreement above to start the automated compliance assessment.")
            
            st.markdown("### How it Works")
            st.markdown(
                """
                The **AI Regulatory Compliance Checker** streamlines legal risk management by performing four key automated steps:
                1. **Type Detection:** Identifies the document type (e.g., Data Processing Agreement, Joint Controller Agreement).
                2. **Clause Extraction:** Uses AI to meticulously extract all contractual clauses and sub-clauses.
                3. **Standard Comparison:** Compares the extracted clauses against pre-approved, up-to-date regulatory templates (e.g., GDPR compliant standards).
                4. **Risk Reporting:** Generates an **overall risk score**, flags potential compliance gaps, and suggests specific amendments.
                """
            )
            

    except Exception as e:
        # Robust error message in the UI
        st.error(f"🔥 An unexpected error occurred during the compliance check. Details: {e}")
        # Send error notification (Now sends errors via SLACK)
        # *** UPDATED LINE ***
        notification.send_notification(
            "🔥 Error Occurred in Document Comparison 🔥", 
            f"An error occurred: {e}", 
            notification_type="error"
        )