from vectorstore.chroma_store import collection


print("Collection:", collection.name)
print("Stored chunks:", collection.count())