# TalentMatrix

An intelligent system that leverages NLP and recommendation algorithms to analyze resumes and match candidates to job vacancies, streamlining the recruitment process and improving hiring efficiency.


## Dataset
The dataset was taken from kaggle competitions. 
1. Job descriptions were extracted from [Scraped job descriptions](https://www.kaggle.com/datasets/marcocavaco/scraped-job-descriptions?resource=download). This contains 4412 job descriptions of various fields.
2. Resume pdfs were extrated from [A Perfect Fit](https://www.kaggle.com/datasets/mukund23/a-perfect-fit).

The dataset has been compiled in the following drive:
[Dataset](https://drive.google.com/drive/folders/1r9C3WWqdnq67fh3Ez-Lj-mJiNkZsR4FW?usp=drive_link)


## Description

1. Embedding Job Descriptions:

- All job descriptions were embedded using the BGE embedding model.
- The resulting embeddings were stored in a Chroma database for efficient querying.

2. Parsing PDFs:

- PDFs were processed using the default MarkItDown PDF parser to extract textual content.

3. Entity Extraction:

- The extracted textual data was passed through a large language model (LLM) to identify and extract relevant entities.

4. Entity Validation:

- The extracted entities were validated using the Pydantic module to ensure they adhered to the expected format and data integrity.

5. Querying the Database:

- The validated entities were used to query the Chroma database, retrieving the top-k most relevant results based on the provided criteria.


## Setup
1. Create venv

2. Install the requirements file

`pip install requirements.txt`

3. First, copy the contents of the config_sample.yaml file into a new file named config.yaml.

4. Run the file

`cd TalentMatrix`

`streamlit run app/run.py`

