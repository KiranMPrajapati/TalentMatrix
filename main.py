import os
import sys
import yaml
import json
import pandas as pd
from src.reader import DOC_READER
from markitdown import MarkItDown

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))

from src.llm_caller import LLM
from src.chroma import setup_chromadb
from utils.resume_validator_and_processor import ResumeProcessor

from flask import Flask, jsonify, request

# Initialize the Flask app
app = Flask(__name__)


with open('config.yaml', 'r') as file:
    CONFIG_DATA = yaml.load(file, Loader=yaml.FullLoader)


# Locate the base TalentMatrix directory
current_dir = os.path.abspath(__file__)  
base_path = os.path.abspath(os.path.join(current_dir, "../../TalentMatrix"))

path_to_jd = os.path.join(base_path, CONFIG_DATA['data_path']['path_to_jd'])
path_to_train_resume = os.path.join(base_path, CONFIG_DATA['data_path']['path_to_train_resume'])
path_to_test_resume = os.path.join(base_path, CONFIG_DATA['data_path']['path_to_test_resume'])
path_to_train_csv = os.path.join(base_path, CONFIG_DATA['data_path']['path_to_train_csv'])
path_to_test_csv = os.path.join(base_path, CONFIG_DATA['data_path']['path_to_test_csv'])

md = MarkItDown()
reader = DOC_READER(md)


llm = LLM()
validator = ResumeProcessor(llm)


chroma_client, collection = setup_chromadb(CONFIG_DATA['chroma']['chroma_db_storage_path'], CONFIG_DATA['chroma']['collection_name'])


def add_jd_collection():
    df = pd.read_csv(f"{CONFIG_DATA['path_to_jd']}/JD_data.csv")

    data = []

    for index, row in df.iterrows():
        value = {'page_content': f"Job: {row['job']}\n Position: {row['position']}\n Location: {row['location']}\n Job Description: {row['description'][0]}", 'idx': index}
        data.append(value)

    chroma_client.add_to_collection(collection=collection, docs=data)
    return "Success"
    


def add_collection(file_path):

    data = [] 
    for file in os.listdir(file_path):
        text = reader.doc_markdown(f"{file_path}/{file}")
        print(text)
        # metadata = llm(text)
        metadata = {'basics': {'name': 'HOWARD GOODMAN', 'position': 'Fresher and NLP Engineer', 'email': 'abc@gmail.com', 'summary': 'test'}, 
        'work': [{'company': 'Zynta Labs', 'title': 'NLP Developer Intern', 'startDate': 'Apr 2019', 'endDate': 'Nov 2019'}], 
        'skills': ['Machine Learning', 'Natural Language Processing', 'Deep Learning', 'Sentiment Analysis', 'Python', 'NLTK', 'BERT', 'GPT', 'XLNet', 'Text Analysis', 'Text Extraction', 'OCR'], 
        'education': [{'school': 'Rajiv Gandhi Memorial University', 'degree': 'B.TECH(Electrical)', 'year': '2020', 'startDate': 'Apr 2019', 'endDate': 'Nov 2019'}], 
        'projects': [{'title': 'abc', 'descriptions': 'Made a embedded device that converted ASL to voice and vice versa in real-time.'}]}
        validator = ResumeProcessor(llm)
        result = validator.validate_and_process(metadata)
        result['page_content'] = text
        data.append(result)

    chroma_client.add_to_collection(collection=collection, docs=data)

def retrieve(resume_path, top_k=2):
    # text = reader.doc_markdown(resume_path)
    # result = llm(text)
    result = {'basics': {'name': 'HOWARD GOODMAN', 'position': 'Fresher and NLP Engineer', 'email': 'abc@gmail.com', 'summary': 'test'}, 
    'work': [{'company': 'Zynta Labs', 'title': 'NLP Developer Intern', 'startDate': 'Apr 2019', 'endDate': 'Nov 2019'}], 
    'skills': ['Machine Learning', 'Natural Language Processing', 'Deep Learning', 'Sentiment Analysis', 'Python', 'NLTK', 'BERT', 'GPT', 'XLNet', 'Text Analysis', 'Text Extraction', 'OCR'], 
    'education': [{'school': 'Rajiv Gandhi Memorial University', 'degree': 'B.TECH(Electrical)', 'year': '2020', 'startDate': 'Apr 2019', 'endDate': 'Nov 2019'}], 
    'projects': [{'title': 'abc', 'descriptions': 'Made a embedded device that converted ASL to voice and vice versa in real-time.'}]}
    # result = validator.validate_and_process(result)
    result = json.dumps(result)
    results = chroma_client.query_collection(collection, result, top_k=top_k)                  

    for doc in results:
        print(f"Query Result: {doc}")
    

def main():
    # add_collection(path_to_train_resume)
    retrieve(f'{CONFIG_DATA['data_path']['path_to_train_resume']}/candidate_000.pdf')



# Route to home page
@app.route('/')
def add_to_collection():
    add_collection(path_to_train_resume)
    return jsonify({"message": "Created collection"})    
    

@app.route('/api/retrieve', methods=['GET'])
def retrieve_collection():
    name = request.args.get('name', 'Guest')  # Get 'name' parameter from the URL
    return jsonify({"greeting": f"Hello, {name}!"})



if __name__ == "__main__":
    main()