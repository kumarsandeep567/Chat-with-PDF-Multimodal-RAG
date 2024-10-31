import streamlit as st
import time  # To simulate loading for summary generation

# Sample document data (replace with actual data from your database)
documents = [
    {"title": "Document 1", "summary": "Brief summary of Document 1", "image_url": "https://via.placeholder.com/150", "pdf_url": "https://example.com/doc1.pdf"},
    {"title": "Document 2", "summary": "Brief summary of Document 2", "image_url": "https://via.placeholder.com/150", "pdf_url": "https://example.com/doc2.pdf"},
    {"title": "Document 3", "summary": "Brief summary of Document 3", "image_url": "https://via.placeholder.com/150", "pdf_url": "https://example.com/doc3.pdf"},
]

# Placeholder function to simulate NVIDIA RAG summary generation (replace with actual NVIDIA RAG call)
def display_summarygeneration_page(document_title):
    time.sleep(2)  # Simulating processing time
    return f"Generated detailed summary for {document_title}"

st.title("Document Summary Generation")

# Document selection dropdown
st.subheader("Select Document")
selected_doc = st.selectbox(
    "Choose a document to view and generate a summary",
    [doc["title"] for doc in documents]
)

# Retrieve the selected document's data
selected_data = next(doc for doc in documents if doc["title"] == selected_doc)

# Display document details
st.image(selected_data["image_url"], width=200)
st.write(f"**Title**: {selected_data['title']}")
st.write(f"[Download PDF]({selected_data['pdf_url']})")

# Summary generation button
if st.button("Generate Summary"):
    with st.spinner("Generating summary..."):
        generated_summary = generate_summary(selected_data['title'])
        st.success("Summary generated successfully!")
        st.write("**Generated Summary**")
        st.write(generated_summary)

        # Download button for the summary
        st.download_button(
            label="Download Summary",
            data=generated_summary,
            file_name=f"{selected_data['title']}_summary.txt",
            mime="text/plain"
        )