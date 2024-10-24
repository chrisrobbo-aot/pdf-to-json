import json
import json5
import os
import re
import pandas as pd



import PyPDF2
from openai import OpenAI

client = OpenAI()
sampleJson=""


def split_pdf_to_text_chunks(file_path, max_pages=100):
    """Splits the PDF file into text chunks, each with a maximum of max_pages pages."""
    pdf_reader = PyPDF2.PdfReader(file_path)
    total_pages = len(pdf_reader.pages)
    text_chunks = []

    for i in range(0, total_pages, max_pages):
        text_chunk = ""
        for j in range(i, min(i + max_pages, total_pages)):
            text_chunk += pdf_reader.pages[j].extract_text()  # Extract text from page
            print ("TEXT CHUNK IS --------------\n" + text_chunk )
        text_chunks.append(text_chunk)

    return text_chunks


def process_chunk_with_openai(prompt, chunk_text):
    """Processes a chunk of text with OpenAI and returns JSON output."""

    print("Submitted to ChatGPT:\n" + prompt )

    messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts structured data from text or csv documents."},
        {"role": "user", "content":\
        f"""{prompt}      
         ```json
        {sampleJson}
         ```
        """ + "\n" + chunk_text}
    ]
    response = ""
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
            response = f"{response}{chunk.choices[0].delta.content}"

    return response


def extract_json_from_response(response_text):
    """Extracts JSON block from a text response."""
    # Use regex to find the JSON block between ```json and ```
    json_match = re.search(r'```json(.*?)```', response_text, re.DOTALL)

    if json_match:
        json_text = json_match.group(1).strip()

        try:
            # Parse and return JSON
            parsed_json = json.loads(json_text)
            return parsed_json
        except json.JSONDecodeError as e:
            print("Failed to parse JSON:", e)
            return None
    else:
        print("No JSON block found in response.")
        return None


def process_large_pdf(file_path):
    """Process a large PDF in chunks and combine the JSON results."""
    text_chunks = split_pdf_to_text_chunks(file_path)
    all_json_results = []
    prompt="""
         Please extract the relevant data from the text document and use it to replace the width, height and length
         for "Concrete Pumper Trucks" in the "commodities" array in the provided json. """

    for chunk in text_chunks:
        json_response = process_chunk_with_openai(prompt, chunk)
        parsed_json = extract_json_from_response(json_response)
        print("json_response--->", json_response)
        try:
            # parsed_json = json.loads(json_response)
            print("parsed_json --->", parsed_json)
            if parsed_json:
                all_json_results.extend(parsed_json)  # Aggregate the results
        except json.JSONDecodeError:
            print("Failed to parse JSON for one chunk:", json_response)
            continue
    #print("@@@@@@@@@@@@@@")
    #print(all_json_results)
    return all_json_results


def process_csv(file_path):
    """Process a CSV and combine JSON results."""
    all_json_results = []
#Load the CSV data
    content = pd.read_csv(file_path, 
                          header=None, 
                          usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21],
                          names=[
                                 "selfIssue",
                                 "commodity", 
                                 "powerUnits",
                                 "CanAddTrailer",
                                 "trailers",
                                 "AllowJeep",
                                 "AllowBooster",
                                 "Lower Mainland H",
                                 "Lower Mainland W",
                                 "Lower Mainland L",
                                 "Kootenay W",
                                 "Kootenay H",
                                 "Kootenay L",
                                 "Peace W",
                                 "Peace H",
                                 "Peace L",
                                 "BC Default W",
                                 "BC Default H",
                                 "BC Default L",
                                 "pf",
                                 "pr",
                                 "PolicyRef"]
                                )
    #print ("CSV content is **************************" + json.dumps(content, indent=2) )
    #print ("CSV content is **************************" + content.to_string() )
    #print (f"{json.dumps (content.to_json(),indent=2)}" )
    #print (f"{content}" )
    #for commodity in content["PolicyRef"]:
    #    print (f"*********PolicyRef********{commodity}" )
    #return
    #file = open(file_path, "r")
    #content = file.read()
    #file.close()
    prompt="""
         Please extract the relevant data from the CSV and replace the dimensions for the trailers allowed for 
         "Concrete Pumper Trucks" in the "commodities" array in the provided json. 
         Use the json elements "powerUnitTypes" and  "trailerTypes" to map  values from csv columns
         "powerUnits" and "trailers" respectively. Use the regions in json element "geographicRegions" to map to
         the regions defined in the csv . 
         Size dimension values in the json in element "sizeDimensions" should be augmented by the size dimensions 
         for geographic regions as defined in the csv file for every commodity. All regions should be represented. 
         Replace any values in the json with those from the csv. 
         Output the mappings used and all elements of the commodities array"""
    json_response = process_chunk_with_openai(prompt, content.to_string())
    parsed_json = extract_json_from_response(json_response)
    #print("json_response--->", json_response)
    try:
        # parsed_json = json.loads(json_response)
        #print("parsed_json --->", parsed_json)
        if parsed_json:
            all_json_results.extend(parsed_json)  # Aggregate the results
    except json.JSONDecodeError:
        print("Failed to parse JSON for one chunk:", json_response)
    #print("@@@@@@@@@@@@@@")
    #print(all_json_results)
    return all_json_results
    
    


if __name__ == "__main__":
    file_path = "chapter-5.pdf"
    csv_path = "os-dimensions-simplified.csv"
    output_file_path = "output.json"
    with open('commodities.json') as f:
        sampleJson = json5.load(f)
        #print (f"""***{sampleJson}""")


    # Process the large PDF and get the complete JSON result
    #full_json_data = process_large_pdf(file_path)
    full_json_data = process_csv(csv_path)

    # Output or save the final JSON result
    print(json.dumps(full_json_data, indent=4))
    with open(output_file_path, 'w') as json_file:
        json.dump(full_json_data, json_file, indent=4)
