from crewai.tools import BaseTool
from pydantic import Field
import json
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class DesignBuilderTool(BaseTool):
    name: str = Field(default="DesignGenerator")
    description: str = Field(default="Genereert het uiteindelijke ontwerp op basis van briefing")

    def _run(self, design_prompt_json: str) -> str:
        try:
            prompt_data = json.loads(design_prompt_json)
            design_prompt = json.dumps(prompt_data, indent=2)
            prompt = (
                "Gebruik onderstaande briefing om een designvoorstel te beschrijven."
                " Geef duidelijke structuur en layout-aanwijzingen."
            )

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Je bent een professionele AI-designer."},
                    {"role": "user", "content": prompt + "\n\n" + design_prompt}
                ]
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return json.dumps({"error": str(e)})