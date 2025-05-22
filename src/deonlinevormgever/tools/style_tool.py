from crewai.tools import BaseTool
from pydantic import Field
import json
import os

class StyleAnalysisTool(BaseTool):
    name: str = Field(default="DesignStyleAnalyzer")
    description: str = Field(default="Analyseert designstijl op basis van klantnaam")

    def _run(self, client_name: str) -> str:
        # Dit is een placeholder. In de praktijk zou je hier eerdere ontwerpen ophalen en analyseren.
        # Bijvoorbeeld: analyseer bestanden uit 'uploads/examples/{client_name}/'
        examples_path = f"uploads/examples/{client_name}"
        if not os.path.exists(examples_path):
            return json.dumps({"error": f"Geen voorbeeldmateriaal gevonden voor {client_name}"})

        # Je zou hier beeldherkenning of LLM-analyses kunnen doen op designkenmerken.
        # Voor nu een gefingeerde analyse:
        return json.dumps({
            "style_keywords": ["minimalistisch", "donkere tinten", "grote typografie"],
            "layout": "Veel witruimte, visuele hiërarchie", 
            "font": "Sans-serif, strak",
            "color_palette": ["#111111", "#333333", "#ff0000"]\
        })