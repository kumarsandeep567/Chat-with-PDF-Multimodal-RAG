import streamlit as st

# Sample document data (replace this with your actual data from Snowflake)
documents = [
    {"title": "Document 1", "summary": "Brief summary of Document 1", "image_url": "https://via.placeholder.com/150", "pdf_url": "https://example.com/doc1.pdf"},
    {"title": "Document 2", "summary": "Brief summary of Document 2", "image_url": "https://via.placeholder.com/150", "pdf_url": "https://example.com/doc2.pdf"},
    {"title": "Document 3", "summary": "Brief summary of Document 3", "image_url": "https://via.placeholder.com/150", "pdf_url": "https://example.com/doc3.pdf"},
    # Add more documents as needed
]

st.title("Document Explorer")

# Display documents in a grid layout
st.subheader("Browse Documents")
cols = st.columns(3)  # Adjust the number based on how many columns you want

for idx, document in enumerate(documents):
    with cols[idx % 3]:  # Place each document in one of the three columns
        st.image(document["image_url"], width=150, caption=document["title"])
        st.write(document["summary"])

# Dropdown selection for document selection
st.subheader("Select Document")
selected_doc = st.selectbox(
    "Choose a document to view more details",
    [doc["title"] for doc in documents]
)

# Retrieve selected document data
selected_data = next(doc for doc in documents if doc["title"] == selected_doc)

# Display document details when "View Details" button is clicked
if st.button("View Details"):
    st.write(f"**Title**: {selected_data['title']}")
    st.write(f"**Summary**: {selected_data['summary']}")
    st.write(f"[Download PDF]({selected_data['pdf_url']})")
