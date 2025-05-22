from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

import json
from bs4 import BeautifulSoup
import os
import time
import re
import requests
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class ToneOfVoiceTool(BaseTool):
    name: str = Field(default="ToneOfVoiceExtractor")
    description: str = Field(default="Extracts tone of voice from a website URL")

    def _run(self, url: str) -> str:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        text = " ".join(p.get_text() for p in soup.find_all("p"))
        prompt = f"""
        Analyze the tone of voice of this website. Return only JSON with 2-3 tone words and a one-sentence explanation.
        Content:
        {text[:4000]}
        """
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a tone of voice analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        result = completion.choices[0].message.content.strip()
        match = re.search(r"```json\s*(\{.*?\})\s*```", result, re.DOTALL)
        return match.group(1) if match else result

