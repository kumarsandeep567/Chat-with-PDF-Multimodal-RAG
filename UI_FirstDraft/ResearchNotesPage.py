import streamlit as st

# Sample data for saved research notes
research_notes = [
    {"document": "Document 1", "question": "What is the impact of X?", "answer": "The impact of X is ..."},
    {"document": "Document 2", "question": "How does Y work?", "answer": "Y works by ..."},
    {"document": "Document 3", "question": "Explain the benefits of Z.", "answer": "The benefits of Z are ..."},
    # Add more entries as needed
]

# Derived notes storage
derived_notes = []

st.title("Research Notes")

# Document Filter
st.subheader("Filter by Document")
document_options = ["All Documents"] + list(set(note["document"] for note in research_notes))
selected_document = st.selectbox("Select Document", document_options)

# Filter research notes by selected document
if selected_document == "All Documents":
    filtered_notes = research_notes
else:
    filtered_notes = [note for note in research_notes if note["document"] == selected_document]

# Search Function
st.subheader("Search Research Notes")
search_query = st.text_input("Search for keywords or phrases")

# Search within research notes
if search_query:
    filtered_notes = [
        note for note in filtered_notes
        if search_query.lower() in note["question"].lower() or search_query.lower() in note["answer"].lower()
    ]

# Display filtered and searched research notes
st.subheader("Research Notes")
if filtered_notes:
    for idx, note in enumerate(filtered_notes):
        st.write(f"**Document**: {note['document']}")
        st.write(f"**Question**: {note['question']}")
        st.write(f"**Answer**: {note['answer']}")
        st.write("---")
else:
    st.write("No research notes found matching the criteria.")

# Indexed Search Option
st.subheader("Indexed Search")
search_scope = st.radio("Search within:", ("Research Notes", "Full Text of Documents", "Both"))

if search_scope == "Research Notes":
    st.write("Currently viewing results only within Research Notes.")
elif search_scope == "Full Text of Documents":
    st.write("Currently viewing results within Full Text of Documents. (Functionality to be implemented)")
elif search_scope == "Both":
    st.write("Currently viewing results within both Research Notes and Full Text of Documents. (Functionality to be implemented)")

# Derived Notes Section
st.subheader("Add Derived Research Notes")
derived_question = st.text_input("Enter derived question")
derived_answer = st.text_area("Enter derived answer")
if st.button("Add Derived Note"):
    if derived_question and derived_answer:
        derived_notes.append({"document": selected_document, "question": derived_question, "answer": derived_answer})
        st.success("Derived note added successfully.")
    else:
        st.warning("Please enter both a question and an answer for the derived note.")

# Display Derived Notes
if derived_notes:
    st.subheader("Derived Notes")
    for idx, note in enumerate(derived_notes):
        st.write(f"**Document**: {note['document']}")
        st.write(f"**Question**: {note['question']}")
        st.write(f"**Answer**: {note['answer']}")
        st.write("---")
