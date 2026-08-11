import os

from google import genai
from dotenv import load_dotenv


load_dotenv()

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing.")


client = genai.Client(
    api_key=GEMINI_API_KEY
)




def generate_rag_answer(
    question,
    retrieved_chunks
):

    if not retrieved_chunks:

        return (
            "I could not find this information "
            "in the provided documents."
        )

    # --------------------------------------------------
    # Build context
    # --------------------------------------------------

    context_parts = []

    for chunk in retrieved_chunks:

        context_parts.append(
            f"""
SOURCE: {chunk["source"]}
PAGE: {chunk["page"]}

{chunk["text"]}
"""
        )

    context = "\n\n---\n\n".join(
        context_parts
    )

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    prompt = f"""
You are AeroMind AI, an AI assistant for
engineering documents.

Answer the user's question using ONLY the
provided document context.

Do not use outside knowledge.

If the answer cannot be found in the provided
context, say:

"I could not find this information in the
provided documents."

When answering:

- Be clear and technically accurate.
- Do not invent facts.
- Keep the answer concise but useful.
- Cite the source filename and page number.
- If multiple sources support the answer, cite them.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    # --------------------------------------------------
    # Gemini
    # --------------------------------------------------

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text