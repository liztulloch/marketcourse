import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()


class RAGService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        self.client = genai.Client(api_key=api_key)

        self.knowledge_dir = (
            Path(__file__).resolve().parent.parent / "Knowledge"
        )


        # Chunk files once when FastAPI starts
        self.chunks = self.load_chunks()

        print(f"Loaded {len(self.chunks)} knowledge chunks")

    def split_into_chunks(
        self,
        text,
        chunk_size=1200,
        overlap=150,
    ):
        """
        Split text into chunks of about 1,200 characters.
        Each chunk overlaps the previous chunk by 150 characters.
        """
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            # Prefer ending at a paragraph boundary
            if end < len(text):
                paragraph_end = text.rfind("\n\n", start, end)

                if paragraph_end > start + 400:
                    end = paragraph_end

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break

            start = max(end - overlap, start + 1)

        return chunks

    def load_chunks(self):
        chunks = []

        for file in sorted(self.knowledge_dir.glob("*.txt")):
            text = file.read_text(encoding="utf-8")

            file_chunks = self.split_into_chunks(text)

            for index, chunk_text in enumerate(file_chunks):
                chunks.append({
                    "source": file.name,
                    "chunk_id": index,
                    "text": chunk_text,
                })

        if not chunks:
            raise ValueError(
                f"No .txt knowledge files found in "
                f"{self.knowledge_dir}"
            )

        return chunks

    def tokenize(self, text):
        stop_words = {
            "a", "an", "and", "are", "as", "at", "be",
            "by", "do", "does", "for", "from", "how",
            "i", "in", "is", "it", "me", "of", "on",
            "or", "that", "the", "this", "to", "what",
            "when", "where", "which", "who", "why",
            "with", "you", "your",
        }

        words = re.findall(r"[a-zA-Z0-9]+", text.lower())

        return {
            word
            for word in words
            if word not in stop_words and len(word) > 1
        }

    def retrieve(self, question, top_k=5):
        question_words = self.tokenize(question)
        scored_chunks = []

        for chunk in self.chunks:
            chunk_words = self.tokenize(chunk["text"])

            matching_words = question_words.intersection(
                chunk_words
            )

            score = len(matching_words)

            if score > 0:
                scored_chunks.append({
                    "score": score,
                    "chunk": chunk,
                })

        scored_chunks.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return [
            item["chunk"]
            for item in scored_chunks[:top_k]
        ]

    def answer(self, question):
        relevant_chunks = self.retrieve(
            question=question,
            top_k=5,
        )

        print(
            f"Question: {question} | "
            f"Retrieved chunks: {len(relevant_chunks)}"
        )

        if not relevant_chunks:
            return {
                "question": question,
                "answer": (
                    "The knowledge base does not contain enough "
                    "information to answer that question."
                ),
                "sources": [],
            }

        context = "\n\n".join(
            (
                f"SOURCE: {chunk['source']} "
                f"(chunk {chunk['chunk_id']})\n"
                f"{chunk['text']}"
            )
            for chunk in relevant_chunks
        )

        sources = sorted({
            chunk["source"]
            for chunk in relevant_chunks
        })

        prompt = f"""
You are Market Course, a stock-market education assistant.

Answer the user's question using only the supplied context.

Rules:
- Explain the concept simply and clearly.
- Do not provide personalized financial advice.
- Do not invent information.
- If the context is insufficient, clearly say so.
- Keep the answer focused on the user's question.

CONTEXT:
{context}

USER QUESTION:
{question}
"""

        print(f"Sending {len(prompt)} prompt characters to Gemini")

        response = self.client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=prompt,
        )

        return {
            "question": question,
            "answer": response.output_text,
            "sources": sources,
        }