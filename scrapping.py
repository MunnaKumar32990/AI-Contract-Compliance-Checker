import requests, json
import data_extraction
# scrape data from different link using get api
def scrape_data(url, name):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(name, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print("Download Successful")
    else:
        print("Failed to download", response.status_code)


def call_scrape_function():
    # nested dict
    DOCUMENT_MAP = {
        # K key : value - {}
        "DPA": {"json_file": "json_files\\dpa.json", "link": "https://www.benchmarkone.com/wp-content/uploads/2018/05/GDPR-Sample-Agreement.pdf"},
        # "C2C": {"json_file": "json_files\\c2c.json", "link": "https://www.fcmtravel.com/sites/default/files/2020-03/2-Controller-to-controller-data-privacy-addendum.pdf"},
        # "JCA": {"json_file": "json_files\\jca.json", "link": "https://www.surf.nl/files/2019-11/model-joint-controllership-agreement.pdf"},
        # "SCC": {"json_file": "json_files\\scc.json", "link": "https://www.proofpoint.com/sites/default/files/legal/pfpt-eu-tc-proofpoint-gdpr-data-processing-agreement-revisions-jul-19-2021.pdf"},
        # "subprocessor": {"json_file": "json_files\\subprocessor.json", "link": "https://greaterthan.eu/wp-content/uploads/Personal-Data-Sub-Processor-Agreement-2024-01-24.pdf"},
    }

    temp_agreement = 'temp_agreement.pdf'

    # Loop Through each document type
    for key in DOCUMENT_MAP:
        # dealing with DPA agreement only
        scrape_data(DOCUMENT_MAP[key]["link"], temp_agreement)
        
        clauses = data_extraction.Clause_extraction(temp_agreement)
        
        # Step 6: Update respective json file with new clauses (dpa.json)
        with open(DOCUMENT_MAP[key]["json_file"], "w", encoding="utf-8") as f:
            json.dump(clauses, f, indent=2, ensure_ascii=False)


# call_scrape_function()

    
