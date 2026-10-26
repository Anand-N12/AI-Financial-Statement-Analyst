
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from langfuse import observe, get_client

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

client = genai.Client(api_key=API_KEY) if API_KEY else None


@observe(name="financial-trend-explanation", as_type="generation")
def explain_financial_trends(financial_summary):

    if not client:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    prompt = f"""
    You are a financial statement analysis assistant.

    Analyze the following calculated financial information:
    {financial_summary}

    Explain:
    1. Profitability trends.
    2. Liquidity and short-term obligations.
    3. Debt and financial risk.
    4. Changes between years.
    5. Warning signs requiring further investigation.

    Rules:
    - Use simple, professional English.
    - Base conclusions only on the supplied data.
    - Never invent financial figures.
    - Mention when a ratio cannot be calculated.
    - Do not present this as professional financial advice.
    """

    response = None

    # Retry temporary Gemini server errors
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            break

        except errors.ServerError:
            if attempt == 2:
                raise

            time.sleep(2 * (attempt + 1))

    answer = response.text or ""
    usage = response.usage_metadata

    # Record token usage in Langfuse
    if usage:
        get_client().update_current_generation(
            model=MODEL_NAME,
            usage_details={
                "input": usage.prompt_token_count or 0,
                "output": usage.candidates_token_count or 0,
                "total": usage.total_token_count or 0,
            },
        )

    if not answer:
        raise ValueError("Gemini returned an empty response.")

    return answer


def flush_langfuse():
    try:
        get_client().flush()
    except Exception as exc:
        print(f"Langfuse flush warning: {exc}")
