from crewai.tools import BaseTool
from pydantic import Field
import json
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class PromptBuilderTool(BaseTool):
    name: str = Field(default="PromptComposer")
    description: str = Field(default="Combineert alle data tot een designbriefing in JSON")

    def _run(self, brandbook_json: str, tone_json: str, goal: str, audience: str, style_json: str) -> str:
        data = {
            "branding": json.loads(brandbook_json),
            "tone_of_voice": json.loads(tone_json),
            "goal": goal,
            "audience": audience,
            "style": json.loads(style_json)
        }

        prompt = (
            "Maak een gestructureerde designbriefing in JSON-formaat op basis van deze input."
            "Gebruik duidelijke instructies voor een grafisch ontwerper."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Je bent een creatieve AI prompt-bouwer."},
                {"role": "user", "content": prompt + "\n\nInput:\n" + json.dumps(data, indent=2)}
            ]
        )

        content = response.choices[0].message.content.strip()
        return content.replace("```json", "").replace("```", "").strip()