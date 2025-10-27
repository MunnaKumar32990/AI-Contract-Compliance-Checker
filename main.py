import streamlit as st
import agreement_comparision
import data_extraction
import json
import schedule
import time
import scrapping
import threading
import notifications as notification


def run_scheduler():
    # schedule.every().day.at("00:00").do(scrapping.call_scrape_function)
    schedule.every(10).seconds.do(scrapping.call_scrape_function)  # run every 10s for testing

    while True:
        schedule.run_pending()
        time.sleep(5)


threading.Thread(target=run_scheduler, daemon=True).start()        

# ******** Phase 3 ******** #
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

    # Streamlit UI Title
        st.title("📑 Contract Compliance Checker")


    # File Upload (PDF only)
        uploaded_file = st.file_uploader("Upload an agreement (PDF only)", type=["pdf"])

        if uploaded_file is not None:
        # Save uploaded file temporarily
            with open("temp_uploaded.pdf", "wb") as f:
                f.write(uploaded_file.read())

            st.info("Processing your file...")

        # Step 1: Identify the type of agreement
            agreement_type = agreement_comparision.document_type("temp_uploaded.pdf")
            st.write("**Detected Document Type:**", agreement_type)

            if agreement_type in AGREEMENT_JSON_MAP:
                # Step 2: Extract clause data from the agreement
                unseen_data = data_extraction.Clause_extraction("temp_uploaded.pdf")
                st.write("**Clause Extraction Completed**")

                # Step 3: Fetch stored template data
                template_file = AGREEMENT_JSON_MAP[agreement_type]
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)

                # Step 4: Compare the unseen data with template data
                result = agreement_comparision.compare_agreements(unseen_data, template_data)

                # Show results
                st.subheader("📊 Comparison Result")
                st.write(result)
                body = f"Agreement type is {agreement_type} \n Comparison Result: {result}"
                notification.send_notification("Agreement Comparison Result", body)



            else:
            # If document type is not recognized
                st.error(f"This Document does not comes under GDPR Compliance")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        notification.send_notification("Error Occured in Document Comparison", f"An error occurred: {e}")
        
