import json
import os
import re

import PyPDF2
from openai import OpenAI

client = OpenAI()


def split_pdf_to_text_chunks(file_path, max_pages=1):
    """Splits the PDF file into text chunks, each with a maximum of max_pages pages."""
    pdf_reader = PyPDF2.PdfReader(file_path)
    total_pages = len(pdf_reader.pages)
    text_chunks = []

    for i in range(0, total_pages, max_pages):
        text_chunk = ""
        for j in range(i, min(i + max_pages, total_pages)):
            text_chunk += pdf_reader.pages[j].extract_text()  # Extract text from page
        text_chunks.append(text_chunk)

    return text_chunks


def process_chunk_with_openai(chunk_text):
    """Processes a chunk of text with OpenAI and returns JSON output."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts structured data from PDF documents."},
        {"role": "user", "content": f"""
            Please extract the relevant data from the PDF and output it in JSON format. The fields to extract include:

            - "Commodity" (name of the commodity being transported)
            - "PowerUnit" (the type of vehicle or tractor used)
            - "CanAddTrailer" (whether a trailer can be added, specify as "Mandatory", "Optional", or "Prohibited")
            - "Trailer" (the type of trailer allowed, if applicable)
            - "AllowJeep" (whether a jeep is allowed, "Yes" or "No")
            - "AllowBooster" (whether a booster is allowed, "Yes" or "No")
            - "LowerMainland" (an object containing "Width", "Height", "Length")
            - "Kootenay" (an object containing "Width", "Height", "Length")
            - "PeaceRegion" (an object containing "Width", "Height", "Length")

            The output should be structured as follows:

            ```json
            [
                {{
                    "Commodity": "Bridge Beams",
                    "PowerUnit": "Truck Tractors",
                    "CanAddTrailer": "Mandatory",
                    "Trailer": "Pole Trailers",
                    "AllowJeep": "Yes",
                    "AllowBooster": "Yes",
                    "LowerMainland": {{
                        "Width": 2.6,
                        "Height": 4.15,
                        "Length": 36
                    }},
                    "Kootenay": {{
                        "Width": 2.6,
                        "Height": 4.15,
                        "Length": 36
                    }},
                    "PeaceRegion": {{
                        "Width": 4.57,
                        "Height": 5.33,
                        "Length": 36
                    }},
                    "PeaceRegion": {{
                        "Width": 4.57,
                        "Height": 5.33,
                        "Length": 36
                    }},
                    "BCDefault": {{
                        "Width": 4.57,
                        "Height": 5.33,
                        "Length": 36
                    }},
                    "Projection": {{
                        "Width": 4.57,
                        "Height": 5.33,
                        "Length": 36
                    }},
                    "PolicyRef": {{
                        "Ref": "4.2.7.A.13"
                    }}
                }},
                {{
                    "Commodity": "Garbage Bins",
                    "PowerUnit": "Truck Tractors",
                    "CanAddTrailer": "Mandatory",
                    "Trailer": "Semi-Trailers",
                    "AllowJeep": "No",
                    "AllowBooster": "No",
                    "LowerMainland": {{
                        "Width": 2.6,
                        "Height": 4.15,
                        "Length": 23
                    }},
                    "Kootenay": {{
                        "Width": 2.6,
                        "Height": 4.15,
                        "Length": 23
                    }},
                    "PeaceRegion": {{
                        "Width": 4.57,
                        "Height": 5.33,
                        "Length": 23
                    }},
                    "BCDefault": {{
                        "Width": 4.57,
                        "Height": 5.33,
                        "Length": 36
                    }},
                    "Projection": {{
                        "Width": 4.57,
                        "Height": 5.33,
                        "Length": 36
                    }},
                    "PolicyRef": {{
                        "Ref": "4.2.7.A.13"
                    }}
                }}
            ]
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

    for chunk in text_chunks:
        json_response = process_chunk_with_openai(chunk)
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
    print("@@@@@@@@@@@@@@")
    print(all_json_results)
    return all_json_results


if __name__ == "__main__":
    file_path = "chapter-5.pdf"
    output_file_path = "output.json"

    # Process the large PDF and get the complete JSON result
    full_json_data = process_large_pdf(file_path)

    # Output or save the final JSON result
    print(json.dumps(full_json_data, indent=4))
    with open(output_file_path, 'w') as json_file:
        json.dump(full_json_data, json_file, indent=4)
