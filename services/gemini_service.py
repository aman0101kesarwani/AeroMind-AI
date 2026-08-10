import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def generate_answer(prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text








# Create a RAG Prompt
def generate_rag_answer(question, retrieved_chunks):

    context = "\n\n".join(
        [
            f"Source: {chunk['source']}\n"
            f"Page: {chunk['page']}\n"
            f"Content: {chunk['text']}"
            for chunk in retrieved_chunks
        ]
    )

    prompt = f"""
You are AeroMind AI, an engineering document assistant.

Answer the user's question using ONLY the provided document context.

If the answer cannot be found in the context, say:
"I could not find this information in the provided documents."

Do not invent information.

User Question:
{question}

Document Context:
{context}

Provide a clear and concise answer.
"""

    return generate_answer(prompt)