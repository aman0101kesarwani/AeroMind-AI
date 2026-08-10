from services.gemini_service import generate_answer


prompt = """
Explain aircraft engine maintenance in simple terms.
Keep the answer under 100 words.
"""

answer = generate_answer(prompt)

print("\nGemini Response:")
print("=" * 60)
print(answer)