from google import genai
from pydantic import BaseModel
import json
import PyPDF2
import os
import notifications as notification
# from groq import Groq
from dotenv import load_dotenv
from google.genai import types

load_dotenv()

# ********   Phase 1    ******** #
def Clause_extraction(file):
    print("inside clause extraction")
    
    class ClauseExtraction(BaseModel):
        clause_id: str
        heading: str
        text: str
    
    text = ""
    with open(file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY2"))
    # client = Groq(
    #     api_key=os.environ.get("GROQ_API_KEY_Kashish"),
    # )
    
    prompt = f"""
    you are an expert in legal contract analysis.
    Your task is to extract all **clauses** from the following contract text.
    ### Guidelines:
    - A clause may begin with:
    - A number/letter (e.g. "1.", "A."),
    - The word "Clause" followed by a number (e.g. "Clause 1", "Clause 5"), OR
    - An ALL CAPS heading (e.g. "DEFINATION", "TRANSFER OF DATA".)

    -Each extracted clause must include:
    -**clause_id** (the exact numbering/label from the contract e.g. "1.", "A.",
    "Clause 1", "EXHIBIT A" etc)
    -**heading/title** (use the explicit heading if present; if absent, use the
    first few words of the clause as a makeshift title)
    -**full text** (the complete text of the clause, including any sub-clauses,
    preserving legal wording exactly as in the contract)

    -Maintain clause boundaries percisly. do not merge multiple clauses into one.
    -Include clauses from exhibits, appendices, and annexes if present.
    -Do not omit any content unless it is clearly not-contractual (e.g. page
    numbers, headers, footers, blank sihnature lines).
    -response in **valid json** only (no explanation, no notes, no extra text).

    Input: {text}

    Response in this JSON Structure:
    [
        {{
            "clause_id": "<clause_id>",
            "heading/title": "<heading_or_title>",
            "full text": "<full_text_of_clause>"
        }},
        ...
    ]
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
            response_mime_type="application/json",
            response_schema=list[ClauseExtraction],
        ),
    )
    
    response = response.text
    print(response)
    
    # chat_completion = client.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt,
    #         }
    #         ],
    #         model="llama-3.3-70b-versatile",
    # )
    # print(chat_completion.choices[0].message.content)
    # response = chat_completion.choices[0].message.content
    
    return response


def Clause_extraction_with_summarization(file):
    print("inside clause extraction")
    class ClauseExtraction(BaseModel):
        clause_id: str
        heading: str
        summarised_text: str
   
    text = ""
    with open(file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
         
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
   
    prompt = f"""
    you are an expert in legal contract analysis.
    Your task is to extract all **clauses** from the following contract text and
    summarise its clause data.
   
    ### Guidelines:
    - A clause may begin with:
    - A number/letter (e.g. "1.", "A."),
    - The word "Clause" followed by a number (e.g. "Clause 1", "Clause 5"), OR

    - An ALL CAPS heading (e.g. "DEFINATION", "TRANSFER OF DATA".)
   
    -Each extracted clause must include:
    -**clause_id** (the exact numbering/label from the contract e.g. "1.", "A.",
    "Clause 1", "EXHIBIT A" etc)
    -**heading/title** (use the explicit heading if present; if absent, use the
    first few words of the clause as a makeshift title)
    -**summarised text** (short and summarise text of the clause, including any
    sub-clauses, preserving legal wording exactly as in the contract, contains only
    important information from the clause and its sub-clauses)
   
    -Maintain clause boundaries percisly. do not merge multiple clauses into one.
    -Include clauses from exhibits, appendices, and annexes if present.
    -Do not omit any content unless it is clearly not-contractual (e.g. page
    numbers, headers, footers, blank sihnature lines).
    -response in **valid json** only (no explanation, no notes, no extra text).
   
    Input: {text}
   
    Response in this JSON Structure:
    [
        {{
            "clause_id": "<clause_id>",
            "heading/title": "<heading_or_title>",
            "summarised_text": "<summarised_text__of_clause>"
        }},
        ...
    ]
    """
    response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
                response_mime_type="application/json",
                response_schema=list[ClauseExtraction],
            ),
           
        )
    response = response.text
    print(response)
    # chat_completion = client.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt,
    #         }
    #     ],
    #     model="llama-3.3-70b-versatile",
    # )
    # print(chat_completion.choices[0].message.content)
    # response=chat_completion.choices[0].message.content
   
    return response

if __name__ == "__main__":

    try:
        # Define a dictionary to map template PDFs to their output JSON filenames
        template_files = {
            "templates/GDPR-Sample-Agreement.pdf": "dpa.json",
            "templates/(JCA) model-joint-controllership-agreement (1).pdf": "jca.json",
            "templates/(C2C) 2-Controller-to-controller-data-privacy-addendum (2).pdf": "c2c.json",
            "templates/(Subprocessing Contract) Personal-Data-Sub-Processor-Agreement-2024-01-24 (1).pdf": "subprocessor.json",
            "templates/(SCCs) Standard Contractual Clauses (1).pdf": "scc.json"
        }

        # Iterate through the dictionary to generate all JSON files
        for pdf_file, json_file in template_files.items():
            print(f"Processing {pdf_file} and generating {json_file}...")
            try:
                # Call the summarization function for the current PDF
                response = Clause_extraction_with_summarization(pdf_file)

                # Save the response to the corresponding JSON file
                with open(json_file, "w", encoding="utf-8") as f:
                    # Need to parse the string response into a JSON object first
                    json_object = json.loads(response)
                    json.dump(json_object, f, indent=2, ensure_ascii=False)

                print(f"Successfully generated {json_file}\n")

            except FileNotFoundError:
                print(f"Error: PDF file '{pdf_file}' not found. Please check the path.\n")
            except json.JSONDecodeError:
                print(f"Error: Failed to parse JSON response from {pdf_file}.\n")
            except Exception as e:
                print(f"An error occurred while processing {pdf_file}: {e}\n")
                notification.send_notification(
                    "Error in Clause Extraction",
                    f"An error occurred while processing {pdf_file}: {e}"
                )

    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        notification.send_notification("Unexpected Script Error", str(e))
