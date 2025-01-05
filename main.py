import os
import yaml
import json
import pandas as pd
import concurrent.futures

from markitdown import MarkItDown

from src.llm_caller import LLM
from src.reader import DOC_READER
from src.chroma import setup_chromadb
from utils.resume_validator_and_processor import ResumeProcessor
from logger_config import get_logger

logger = get_logger("MainModule")

# Load configuration file
def load_config(path='config.yaml'):
    with open(path, 'r') as file:
        CONFIG_DATA = yaml.load(file, Loader=yaml.FullLoader)
    return CONFIG_DATA

current_dir = os.path.abspath(__file__)
base_path = os.path.abspath(os.path.join(current_dir, "../../TalentMatrix"))

CONFIG_DATA = load_config(path='config.yaml')

path_to_jd = os.path.join(base_path, CONFIG_DATA['data_path']['path_to_jd'])
path_to_train_resume = os.path.join(base_path, CONFIG_DATA['data_path']['path_to_train_resume'])
path_to_test_resume = os.path.join(base_path, CONFIG_DATA['data_path']['path_to_test_resume'])
path_to_train_csv = os.path.join(base_path, CONFIG_DATA['data_path']['path_to_train_csv'])
path_to_test_csv = os.path.join(base_path, CONFIG_DATA['data_path']['path_to_test_csv'])

md = MarkItDown()
reader = DOC_READER(md)
llm = LLM()
validator = ResumeProcessor(llm)
chroma_client, collection = setup_chromadb(
    CONFIG_DATA['chroma']['chroma_db_storage_path'], CONFIG_DATA['chroma']['collection_name']
)

def add_jd_collection(jd_path="JD_data.csv"):
    """Add job descriptions to the ChromaDB collection."""
    df = pd.read_csv(os.path.join(path_to_jd, jd_path))
    data = []

    for index, row in df.iterrows():
        value = {
            'page_content': f"Job: {row['job']}\nPosition: {row['position']}\nLocation: {row['location']}\nJob Description: {row['description'][0]}",
            'idx': index
        }
        data.append(value)

    chroma_client.add_to_collection(collection=collection, docs=data)
    return "Success"
    

def add_collection(file_path):
    """Add resumes to the ChromaDB collection."""
    data = []
    for file in os.listdir(file_path):
        result = reader.doc_markdown(os.path.join(file_path, file))
        result['page_content'] = result
        data.append(result)

    chroma_client.add_to_collection(collection=collection, docs=data)
    logger.info(f"Successfully added {file_path} to chroma database")

    return "Success"

def retrieve(resume_path, top_k=2):
    """Retrieve the most relevant job descriptions for a given resume."""
    text = reader.doc_markdown(resume_path)
    result = llm(text)  
    result, flag = validator.validate_and_process(result)
    if flag == False:
        logger.error(result)
        return result

    results = chroma_client.query_collection(collection, json.dumps(result), top_k=top_k)

    for doc in results:
        print(f"Query Result: {doc}")
    
    logger.info(f"Retrieval of most relevant job descriptions for {resume_path}")

    return results


def process_resume(resume_path, top_k=2):
    try:
        results = retrieve(resume_path, top_k=top_k)
        return {resume_path: results}
    except Exception as e:
        logger.error(f"Error processing {resume_path}: {e}")
        return {resume_path: None}

def process_resumes_in_parallel(resume_paths, top_k=2, max_workers=2):
    """Process multiple resumes in parallel."""
    resume_files = []
    for files in os.listdir(resume_paths):
        if '.pdf' in files:
            resume_files.append(f"{resume_paths}/{files}")

    if not resume_files:
        logger.error('File not found')
        raise ValueError("No resume files provided. Please ensure the list of resumes is not empty.")

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_resume = {executor.submit(process_resume, path, top_k): path for path in resume_files}
        for future in concurrent.futures.as_completed(future_to_resume):
            resume_path = future_to_resume[future]
            try:
                result = future.result()
                results.update(result)
            except Exception as e:
                logger.error(f"Error retrieving results for {resume_path}: {e}")
    
    return results


if __name__ == "__main__":
    resume_paths = "/home/kiran/assignment/TalentMatrix/data/dataset/test_resumes"
    top_k_results = process_resumes_in_parallel(resume_paths, top_k=2, max_workers=os.cpu_count())
    print(top_k_results)

    result = add_collection(path_to_train_resume)

    # Retrieve example
    resume_path = 'candidate_000.pdf'
    retrieve(os.path.join(path_to_train_resume, resume_path))