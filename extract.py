import json
import os
import re

from groq import Groq
from dotenv import load_dotenv
from tqdm import tqdm
from tenacity import retry, wait_exponential, stop_after_attempt

from schemas import ExtractionResult
from prompts import SYSTEM_PROMPT


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ----------------------------
# Load data
# ----------------------------

def load_emails():
    with open("data/emails_input.json") as f:
        return json.load(f)


def load_ports():
    with open("data/port_codes_reference.json") as f:
        return json.load(f)


# ----------------------------
# Normalize port codes
# ----------------------------

def normalize_port_code(code, ports):

    if not code:
        return None, None

    code = code.strip().upper()

    matches = []

    for port in ports:

        if port["code"] == code:
            matches.append(port)

        elif port["code"].endswith(code):
            matches.append(port)

        elif code in port["name"].upper():
            matches.append(port)

    if not matches:
        return None, None

    # choose canonical (shortest) name
    best = sorted(matches, key=lambda x: len(x["name"]))[0]

    return best["code"], best["name"]


# ----------------------------
# Fallback port detection
# ----------------------------

def fallback_port_from_text(text, ports):

    text = text.lower()

    for port in ports:
        if port["name"].lower() in text:
            return port["code"], port["name"]

    return None, None


# ----------------------------
# LLM Call
# ----------------------------

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def call_llm(subject, body):

    prompt = f"""
Subject:
{subject}

Body:
{body}

Extract shipment details and return ONLY JSON.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content


# ----------------------------
# JSON cleaner
# ----------------------------

def parse_llm_json(text):

    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        json_text = text[start:end]

        return json.loads(json_text)

    except Exception as e:

        print("\nJSON PARSE ERROR")
        print("Error:", e)
        print("Raw LLM output:\n", text)

        return {}


# ----------------------------
# Main extraction
# ----------------------------

def main():

    emails = load_emails()
    ports = load_ports()

    results = []

    for email in tqdm(emails):

        email_id = email["id"]
        subject = email["subject"]
        body = email["body"]

        try:

            llm_output = call_llm(subject, body)

            # print("\n-----------------------------")
            # print("EMAIL:", email_id)
            # print("LLM RESPONSE:")
            # print(llm_output)
            # print("-----------------------------")

            data = parse_llm_json(llm_output)

            # normalize ports from LLM output
            origin_code, origin_name = normalize_port_code(
                data.get("origin_port_code"), ports
            )

            dest_code, dest_name = normalize_port_code(
                data.get("destination_port_code"), ports
            )

            combined_text = subject + " " + body

            # fallback if LLM fails
            if origin_code is None:
                origin_code, origin_name = fallback_port_from_text(combined_text, ports)

            if dest_code is None:
                dest_code, dest_name = fallback_port_from_text(combined_text, ports)

            result = ExtractionResult(
                id=email_id,
                product_line=data.get("product_line"),
                origin_port_code=origin_code,
                origin_port_name=origin_name,
                destination_port_code=dest_code,
                destination_port_name=dest_name,
                incoterm=data.get("incoterm"),
                cargo_weight_kg=data.get("cargo_weight_kg"),
                cargo_cbm=data.get("cargo_cbm"),
                is_dangerous=data.get("is_dangerous"),
            )

        except Exception as e:

            print("\nERROR PROCESSING EMAIL:", email_id)
            print("Error:", e)

            result = ExtractionResult(id=email_id)

        results.append(result.model_dump())

    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nExtraction complete. Output saved to output.json")


if __name__ == "__main__":
    main()