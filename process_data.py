import json
import os
import time
import re
from google import genai
from google.genai import types

# Initialize Vertex AI Gemini Client
client = genai.Client(
    vertexai=True,
    project="hack-the-law25cam-501",
    location="global",
)

def normalize_text(value):
    """Convert lists or nulls to clean strings"""
    if value is None:
        return ""
    elif isinstance(value, list):
        return "\n".join(str(item) for item in value)
    elif isinstance(value, dict):
        return json.dumps(value, indent=2)
    return str(value)


def process_with_llm(case_json):
    case_id = case_json.get("Identifier", "")
    title = case_json.get("Title", "")

    # Extract content from decisions/opinions
    # Collect all available opinion content
    case_text = ""
    for decision in case_json.get("Decisions", []):
        for opinion in decision.get("Opinions", []):
            if opinion.get("Content"):
                case_text += opinion["Content"] + "\n"

    print(case_text)

    # Truncate
    max_text_length = 80000
    if len(case_text) > max_text_length:
        case_text = case_text[:max_text_length]

    # Prompt
    prompt = f"""
You are a legal expert in international arbitration. Analyze the following JSON-formatted arbitration case and extract key structured information as described.

Please extract:

1. CASE_FACTS — summary of the main facts (background, dispute, actions)
2. RELEVANT_TREATY_ARTICLES — list of relevant treaty article names or numbers (e.g., "Article 5")
3. CLAIMS_ACCUSATIONS — list of alleged violations (e.g., expropriation)
4. AWARD_INFORMATION — any monetary awards (amount + currency)
5. FACT_COMPONENTS — split into:
   a) SUBJECTIVE_COMPONENT — intentions/motivations
   b) OBJECTIVE_COMPONENT — factual events/actions
   c) CIRCUMSTANTIAL_COMPONENT — context, outcomes, external factors

Here is the case data:
```json
{json.dumps(case_json, indent=2)}
```
Respond in valid JSON only. No markdown, no prose, no explanation.
"""

    try:
        # Build prompt content
        contents = [types.Content(
                        role="user",
                        parts=[types.Part(text=prompt)]
                    )]


        # Generation config
        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=8192,
            safety_settings=[
                types.SafetySetting(category=cat, threshold="OFF") for cat in [
                    "HARM_CATEGORY_HATE_SPEECH",
                    "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "HARM_CATEGORY_HARASSMENT"
                ]
            ],
            thinking_config=types.ThinkingConfig(thinking_budget=-1)
        )

        # Call Vertex AI Gemini
        response_chunks = client.models.generate_content_stream(
            model="gemini-2.5-flash",  # Or use gemini-1.5-pro
            contents=contents,
            config=config,
        )

        # Combine response stream
        # full_response = "".join(chunk.text for chunk in response_chunks)
        # extraction_result = json.loads(full_response)

        full_response = "".join(chunk.text for chunk in response_chunks)

        # 🔍 Print raw Gemini response for debugging
        print("\n--- RAW GEMINI RESPONSE ---\n")
        print(full_response)
        print("\n--- END RESPONSE ---\n")

        # Remove markdown code block formatting if present
        cleaned = full_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]  # remove the ```json
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]  # remove the ending ```

        extraction_result = json.loads(cleaned)


        # RLJP output format
        return {
            "fact": normalize_text(extraction_result.get("CASE_FACTS")),
            "meta": {
                "relevant_articles": extraction_result.get("RELEVANT_TREATY_ARTICLES", []),
                "accusation": extraction_result.get("CLAIMS_ACCUSATIONS", ""),
                "term_of_imprisonment": {
                    "death_penalty": False,
                    "imprisonment": extract_award_amount(extraction_result.get("AWARD_INFORMATION", "")),
                    "life_imprisonment": False
                },
                "applicable_treaties": case_json.get("ApplicableTreaties", []),
                "party_nationalities": case_json.get("PartyNationalities", []),
                "status": case_json.get("Status", "")
            },
            "caseID": case_id,
            "fact_split": { 
                "zhuguan": normalize_text(extraction_result.get("FACT_COMPONENTS", {}).get("SUBJECTIVE_COMPONENT")),
                "keguan": normalize_text(extraction_result.get("FACT_COMPONENTS", {}).get("OBJECTIVE_COMPONENT")),
                "shiwai": normalize_text(extraction_result.get("FACT_COMPONENTS", {}).get("CIRCUMSTANTIAL_COMPONENT")),
            }
        }

    except Exception as e:
        print(f"Error processing case {case_id}: {str(e)}")
        return None

def extract_award_amount(award_text):
    if isinstance(award_text, (int, float)):
        return award_text
    if isinstance(award_text, str):
        amounts = re.findall(r'(\d+(?:\.\d+)?)\s*(million|billion)?', award_text.lower())
        if amounts:
            value, multiplier = amounts[0]
            value = float(value)
            if 'million' in multiplier:
                value *= 1_000_000
            elif 'billion' in multiplier:
                value *= 1_000_000_000
            return value
    return 0

def process_jusmundi_dataset(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    rljp_cases = []

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(input_dir, filename)
            print(f"Processing {filename}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                case_json = json.load(f)
            rljp_case = process_with_llm(case_json)
            if rljp_case:
                rljp_cases.append(rljp_case)
            time.sleep(1)

    with open(os.path.join(output_dir, "testset.json"), 'w', encoding='utf-8') as f:
        json.dump(rljp_cases, f, indent=2)
    with open(os.path.join(output_dir, "testset_fact_split.json"), 'w', encoding='utf-8') as f:
        json.dump(rljp_cases, f, indent=2)

    print(f"Processed {len(rljp_cases)} cases to {output_dir}")


if __name__ == "__main__":
    input_dir = "./jus_mundi_hackathon_data/cases/"
    output_dir = "./data/testset/jusmundi/"
    process_jusmundi_dataset(input_dir, output_dir)
