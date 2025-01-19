import os
import sys
import streamlit as st

from markitdown import MarkItDown

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


from reader import DOC_READER
from config import CONFIG_DATA
from main import retrieve, add_jd_collection


current_dir = os.path.abspath(__file__)
base_path = os.path.abspath(os.path.join(current_dir, "../../"))

os.makedirs(os.path.join(base_path,f"{CONFIG_DATA['data_path']['upload_path']}"), exist_ok=True) 


md = MarkItDown()
doc_reader = DOC_READER(md)



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

    uploaded_resume_file = st.file_uploader("Choose a resume (PDF format) to extract top k job matches", type=["pdf"])

    if uploaded_resume_file is not None:
        st.write(f"Uploaded file: {uploaded_resume_file.name}")

        save_uploaded_file(uploaded_resume_file)
        results = retrieve(os.path.join(base_path,f"{CONFIG_DATA['data_path']['upload_path']}/{uploaded_resume_file.name}"))
        if results: 
            st.write("Outputs:")
            st.write(results)

    uploaded_jd_file = st.file_uploader("Choose job descriptions (CSV format) to save it in the database", type=["csv"])

    if uploaded_jd_file is not None:
        st.write(f"Uploaded file: {uploaded_jd_file.name}")

        save_uploaded_file(uploaded_jd_file)
        result = add_jd_collection(os.path.join(base_path,f"{CONFIG_DATA['data_path']['upload_path']}/{uploaded_jd_file.name}"))
        st.write(result)

if __name__ == "__main__":
    main()
