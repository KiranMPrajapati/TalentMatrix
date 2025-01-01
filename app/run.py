import os
import sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from reader import doc_markdown


def save_uploaded_file(uploaded_file):
    try:
        # Create a file path to save the uploaded file
        with open(f"data/uploaded/{uploaded_file.name}", "wb") as f:
            # Write the content of the uploaded file to the file
            f.write(uploaded_file.getbuffer())
        return f"File saved at: uploaded_files/{uploaded_file.name}"
    except Exception as e:
        return f"Error saving file: {e}"


def main():
    st.title("TalentMatrix")
    st.write("""An intelligent system that leverages NLP and recommendation algorithms to analyze resumes 
             and match candidates to job vacancies, streamlining the recruitment process and improving hiring efficiency.""")


    uploaded_file = st.file_uploader("Choose a file", type=["pdf"])

    if uploaded_file is not None:
        st.write(f"Uploaded file: {uploaded_file.name}")

        save_uploaded_file(uploaded_file)
        content = doc_markdown(f"data/uploaded/{uploaded_file.name}")
        st.write(content.text_content)

if __name__ == "__main__":
    main()
