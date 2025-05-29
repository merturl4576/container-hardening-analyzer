
import openai
import os
import json
from models.finding import Finding
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_gpt_suggestions(content):
    try:
        prompt = f"""Analyze this Dockerfile or Kubernetes YAML for real-world security issues.
Respond in JSON format like:
[
  {{"level":"HIGH", "message":"Issue", "suggestion":"Fix"}}
]
Content:
{content}
"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        items = json.loads(response['choices'][0]['message']['content'])
        return [Finding(i["level"], i["message"], i["suggestion"]) for i in items]
    except Exception as e:
        print("GPT error:", e)
        return []
