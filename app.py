import streamlit as st
from overview import display_overview_page
from documentexplorer import display_document_explorer
from summarygenerate import display_summarygeneration_page
# from qainterface import display_qainterface_page
# from reportgeneration import display_reportgeneration_page

def main():
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state['page'] = 'overview'  # Set overview as the default page

    # Sidebar for navigation (only after login)
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        st.sidebar.title("Navigation")
        nav_option = st.sidebar.radio(
            "Choose a page:",
            ('Document Explorer', 'Summary Generation')
        )

        # Update session state based on sidebar selection
        if nav_option == 'Document Explorer':
            st.session_state['page'] = 'documentexplorer'
        elif nav_option == 'Summary Generation':
            st.session_state['page'] = 'summarygeneration'
        elif nav_option == 'QA Interface':
            st.session_state['page'] = 'qainterface'
        elif nav_option == 'Report Generation':
            st.session_state['page'] = 'reportgeneration'    

    # Display the appropriate page based on session state
    if st.session_state['page'] == 'overview':
        display_overview_page()
    elif st.session_state['page'] == 'documentexplorer':
        display_document_explorer()
    elif st.session_state['page'] == 'summarygeneration':
        display_summarygeneration_page()
    # elif st.session_state['page'] == 'qainterface':
    #     display_qainterface_page()
    # elif st.session_state['page'] == 'reportgeneration':
    #     display_reportgeneration_page()    

if __name__ == '__main__':
    main()
