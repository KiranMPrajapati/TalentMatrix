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

6. Save the data to postgresql database

- The final results were saved to a PostgreSQL database. This included creating appropriate tables, ensuring indexing for faster query performance.


## Setup
1. Create venv

2. Install the requirements file

`pip install -r requirements.txt`

3. First, copy the contents of the config_sample.yaml file into a new file named config.yaml.

4. Run the file

`cd TalentMatrix`

`streamlit run app/run.py`

## Evaluation 
For evaluation, I am using [TorchMetrics](https://lightning.ai/docs/torchmetrics/stable/), a library that provides a wide range of metrics for machine learning models in PyTorch. TorchMetrics ensures consistency and reliability in metric computation across training, validation, and testing phases.

Steps for Evaluation:

1. Metric Initialization:

- The required metrics (e.g., accuracy, precision, recall, F1 score, or regression metrics like mean absolute error) are initialized using TorchMetrics.

2. Threshold for Similarity Score:

- A similarity score threshold of 0.8 has been chosen for evaluation.
- If the model predicts a similarity score greater than 0.8, it is assumed to be a correct sample.
- This threshold helps determine whether a prediction aligns well with the ground truth.

