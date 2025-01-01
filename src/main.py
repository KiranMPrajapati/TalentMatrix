import os
import sys
from reader import DOC_READER
from markitdown import MarkItDown

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))

from llm_caller import LLM
from resume_validator_and_processor import ResumeProcessor


# Locate the base TalentMatrix directory
current_dir = os.path.abspath(__file__)  # Absolute path of the current script
base_path = os.path.abspath(os.path.join(current_dir, "../../../TalentMatrix"))

# Constructing paths relative to the root TalentMatrix directory
path_to_jd = os.path.join(base_path, "data/dataset/jobDescriptions")
path_to_train_resume = os.path.join(base_path, "data/dataset/trainResumes")
path_to_test_resume = os.path.join(base_path, "data/dataset/testResumes")
path_to_train_csv = os.path.join(base_path, "data/dataset/train.csv")
path_to_test_csv = os.path.join(base_path, "data/dataset/test.csv")

md = MarkItDown()

llm = LLM()

def doc_markdown(file_path):
    reader = DOC_READER(md)
    for file in os.listdir(file_path):
        text = reader.doc_markdown(f"{file_path}/{file}")
        print(text)
        resume_schema = llm(text)
        # resume_schema = {'basics': {'name': 'HOWARD GOODMAN', 'position': 'Fresher and NLP Engineer', 'email': 'abc@gmail.com', 'summary': 'test'}, 
        # 'work': [{'company': 'Zynta Labs', 'title': 'NLP Developer Intern', 'startDate': 'Apr 2019', 'endDate': 'Nov 2019'}], 
        # 'skills': ['Machine Learning', 'Natural Language Processing', 'Deep Learning', 'Sentiment Analysis', 'Python', 'NLTK', 'BERT', 'GPT', 'XLNet', 'Text Analysis', 'Text Extraction', 'OCR'], 
        # 'education': [{'school': 'Rajiv Gandhi Memorial University', 'degree': 'B.TECH(Electrical)', 'year': '2020', 'startDate': 'Apr 2019', 'endDate': 'Nov 2019'}], 
        # 'projects': [{'title': 'abc', 'descriptions': 'Made a embedded device that converted ASL to voice and vice versa in real-time.'}]}
        validator = ResumeProcessor(llm)
        result = validator.validate_and_process(resume_schema)
        print(result)


if __name__ == "__main__":
    doc_markdown(path_to_train_resume)