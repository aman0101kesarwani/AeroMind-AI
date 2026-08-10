from vectorstore.chroma_store import document_exists


source = "Engine-Maintenance-Manual.pdf"

exists = document_exists(source)

print("Document:", source)
print("Already indexed:", exists)