from vectorstore.chroma_store import collection


results = collection.get(
    include=["metadatas"]
)

sources = set()

for metadata in results["metadatas"]:
    sources.add(metadata["source"])


print("\nINDEXED DOCUMENTS")
print("=" * 50)

for source in sorted(sources):
    print(source)