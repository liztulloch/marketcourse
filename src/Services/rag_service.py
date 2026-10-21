import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class RAGService:
    def __init__(self):
        self.knowledge_dir = Path(__file__).parent.parent / "Knowledge"

    def load_knowledge(self):
        knowledge = []

        for file in self.knowledge_dir.glob("*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                knowledge.append(
                    f"SOURCE: {file.name}\n{f.read()}"
                )

        return "\n\n".join(knowledge)

    def answer(self, question):
        knowledge = self.load_knowledge()

        prompt = f"""
You are Market Course, a stock market education assistant.

Use the knowledge base below to answer the user's question.

Explain concepts simply and clearly.
Do not provide personalized financial advice.
If the answer is not contained in the knowledge base, say that the
knowledge base does not contain enough information.

KNOWLEDGE BASE:

{knowledge}

USER QUESTION:

{question}
"""

        response = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt
        )

        return {
            "question": question,
            "answer": response.output_text
        }