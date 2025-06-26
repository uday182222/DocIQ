import os
import openai
import json
from pathlib import Path


def extract_fields_from_text(text: str, prompt_content: str):
    """
    Takes the prompt content, appends the document text, calls OpenAI ChatCompletion API (gpt-4o-mini),
    and parses/returns the structured JSON from the LLM response.
    """
    # 1. Insert the text into the prompt (replace {{OCR_TEXT}} or similar)
    if "{{OCR_TEXT}}" in prompt_content:
        prompt = prompt_content.replace("{{OCR_TEXT}}", text)
    else:
        prompt = prompt_content + "\n-----\n" + text

    # 2. Call OpenAI ChatCompletion API
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful document parser. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=2048
    )
    content = response.choices[0].message.content

    # 3. Parse and return JSON
    try:
        # Find the first and last curly braces to extract JSON
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            json_str = content[start:end]
            return json.loads(json_str)
        # Fallback: try to parse the whole content
        return json.loads(content)
    except Exception as e:
        raise RuntimeError(f"Failed to parse LLM JSON output: {e}\nRaw output: {content}") 