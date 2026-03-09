# Freight Email Extraction (LLM)
This project extracts structured shipment information from freight inquiry emails using a Large Language Model (LLM).
The system processes email text and produces structured JSON output containing shipment details such as ports, incoterms, cargo weight, and volume.

## Setup
# create virtual env
    python -m venv venv
    venv\scripts\activate
# Install dependencies
    pip install -r requirements.txt
# Create GROQ_API_KEY
# Create `.env`
    GROQ_API_KEY=your_key
# Run extraction
    python extract.py

    # This generates
    output.json
# Evaluate accuracy
    python evaluate.py


---

# Approach

We use Groq Llama 3.1 70B to extract shipment information from emails.

The pipeline:

1. Load emails
2. Send subject + body to LLM
3. Extract JSON
4. Match ports from reference
5. Validate with Pydantic
6. Save output
7. Evaluate accuracy

---



# Prompt Strategy
    A system prompt is used to instruct the LLM to extract shipment fields in strict JSON format.
    Key design choices:
    temperature set to 0 for deterministic outputs
    request JSON-only responses
    schema-aligned field names
    extraction based on email subject + body


# Result
# Final evaluation score
    Overall Accuracy: 0.86