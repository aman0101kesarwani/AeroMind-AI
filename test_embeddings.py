from embeddings.embedding_model import generate_embeddings


texts = [
    "The aircraft engine requires regular inspection.",
    "Engine maintenance should be performed according to the maintenance schedule.",
    "The weather is sunny today."
]


embeddings = generate_embeddings(texts)


print("Type:", type(embeddings))
print("Shape:", embeddings.shape)

print("\nFirst embedding:")
print(embeddings[0][:10])