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


class BrandbookAnalysisTool(BaseTool):
    name: str = Field(default="BrandbookPDFAnalyzer")
    description: str = Field(default="Analyzes a PDF brandbook and returns branding details in JSON")

    def _run(self, pdf_path: str) -> str:
        try:
            with open(pdf_path, "rb") as f:
                uploaded = client.files.create(file=f, purpose="assistants")
            assistant = client.beta.assistants.create(
                model="gpt-4o",
                name="Brandbook Assistant",
                instructions=(
                    "Analyze this brandbook and return structured JSON:\n"
                    "1. Primary/secondary colors (HEX)\n"
                    "2. Fonts used\n"
                    "3. Logo guidelines\n"
                    "4. Visual style (3 sentences)"
                ),
                tools=[{"type": "file_search"}]
            )
            thread = client.beta.threads.create()
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="Please analyze this PDF.",
                attachments=[
                    {"file_id": uploaded.id, "tools": [{"type": "file_search"}]}
                ]
            )
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )

            waited = 0
            while True:
                status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if status.status == "completed":
                    break
                elif status.status in ["failed", "cancelled", "expired"]:
                    return json.dumps({"error": f"Run status: {status.status}"})
                time.sleep(1)
                waited += 1
                if waited > 60:
                    return json.dumps({"error": "Timeout"})
            
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            content = messages.data[0].content[0].text.value.strip()
            match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
            return match.group(1) if match else content
        except Exception as e:
            return json.dumps({"error": str(e)})
