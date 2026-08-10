from vectorstore.supabase_vector_store import (
    create_document,
    document_exists,
    get_indexed_documents
)


filename = "test-document.pdf"

print(
    "Already exists:",
    document_exists(filename)
)


if not document_exists(filename):

    document = create_document(
        filename,
        f"uploaded-pdfs/{filename}"
    )

    print("Created document:")
    print(document)


print("\nIndexed documents:")

print(
    get_indexed_documents()
)