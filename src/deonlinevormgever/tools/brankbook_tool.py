from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

import json
import os
import time
import re
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


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
