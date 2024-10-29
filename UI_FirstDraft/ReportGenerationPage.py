import streamlit as st
from fpdf import FPDF  # Install this library with 'pip install fpdf2' for PDF generation

# Sample report data
report_data = {
    "summary": "This is a summary of the document...",
    "full_analysis": "This is a full document analysis...",
    "qa_responses": [
        {"question": "What is the impact of X?", "answer": "The impact of X is ..."},
        {"question": "How does Y work?", "answer": "Y works by ..."},
    ],
    "graphs_links": [
        {"name": "Impact of X Graph", "link": "https://example.com/graph1"},
        {"name": "Y Analysis Table", "link": "https://example.com/table1"},
    ]
}

st.title("Report Generation")

# Report Format Selection
st.subheader("Select Report Format")
report_format = st.selectbox(
    "Choose report format",
    ["Summary", "Full Document Analysis", "Q/A Responses"]
)

# Display Report Content Based on Selection
st.subheader("Generated Report")
if report_format == "Summary":
    st.write(report_data["summary"])
elif report_format == "Full Document Analysis":
    st.write(report_data["full_analysis"])
elif report_format == "Q/A Responses":
    for qa in report_data["qa_responses"]:
        st.write(f"**Q:** {qa['question']}")
        st.write(f"**A:** {qa['answer']}")
        st.write("---")

# Graph/Table Links for Visual Data
st.subheader("Relevant Graphs and Tables")
if report_data["graphs_links"]:
    for item in report_data["graphs_links"]:
        st.write(f"[{item['name']}]({item['link']})")

# Report Download Option
def generate_pdf(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, report_text)
    return pdf

st.subheader("Download Report")
download_format = st.selectbox("Select download format", ["PDF", "Text"])

# Prepare the report content based on selected format
if report_format == "Summary":
    report_content = report_data["summary"]
elif report_format == "Full Document Analysis":
    report_content = report_data["full_analysis"]
elif report_format == "Q/A Responses":
    report_content = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in report_data["qa_responses"]])

# Download button
if st.button("Download Report"):
    if download_format == "PDF":
        pdf = generate_pdf(report_content)
        pdf_output = pdf.output(dest="S").encode("latin1")
        st.download_button(label="Download PDF", data=pdf_output, file_name="report.pdf", mime="application/pdf")
    elif download_format == "Text":
        st.download_button(label="Download Text File", data=report_content, file_name="report.txt", mime="text/plain")
