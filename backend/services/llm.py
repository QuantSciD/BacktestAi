import os
from typing import Dict, List

from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)



def generate_experiment_suggestions(metrics: Dict, bias_flags: List[str]) -> List[Dict]:
    prompt = f"""
You are a quantitative trading coach.

Backtest metrics:
{metrics}

Bias flags:
{bias_flags}

Task:
1. Propose 3 concrete next-step experiments to run on this strategy.
2. For each experiment, provide:
   - title
   - description (what to change and why)
   - risk_note (explicit risk / bias warnings).
3. Be concise and practical.

Return ONLY JSON: a list of 3 objects with keys: title, description, risk_note.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    content = response.choices[0].message.content

    import json

    try:
        suggestions = json.loads(content)
    except Exception:
        suggestions = [
            {
                "title": "Review backtest configuration",
                "description": content,
                "risk_note": "LLM output not structured as JSON; please interpret manually.",
            }
        ]
    return suggestions
