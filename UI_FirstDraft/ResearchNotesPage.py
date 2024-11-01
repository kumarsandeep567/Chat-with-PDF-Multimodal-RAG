import streamlit as st

# Sample data for saved research notes
research_notes = [
    {"document": "Document 1", "question": "What is the impact of X?", "answer": "The impact of X is ..."},
    {"document": "Document 2", "question": "How does Y work?", "answer": "Y works by ..."},
    {"document": "Document 3", "question": "Explain the benefits of Z.", "answer": "The benefits of Z are ..."},
]

# Derived notes storage
derived_notes = []

def display_research_notes_page():
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

    # Display Research Notes
    if filtered_notes:
        for note in filtered_notes:
            st.write(f"**Document**: {note['document']}")
            st.write(f"**Question**: {note['question']}")
            st.write(f"**Answer**: {note['answer']}")
            st.write("---")
    else:
        st.write("No research notes found for the selected document.")

    # Option to save new notes
    st.subheader("Save New Research Note")
    new_question = st.text_input("Enter new question")
    new_answer = st.text_area("Enter answer for the new question")

    if st.button("Save Note"):
        if new_question and new_answer:
            new_note = {"document": selected_document, "question": new_question, "answer": new_answer}
            derived_notes.append(new_note)
            st.success("Note saved successfully!")
        else:
            st.warning("Both question and answer fields must be filled.")
