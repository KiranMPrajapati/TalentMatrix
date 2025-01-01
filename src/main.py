import os
from reader import DOC_READER
from markitdown import MarkItDown


path_to_jd = "/home/kiran/assignment/TalentMatrix/data/dataset/jobDescriptions"
path_to_train_resume = "/home/kiran/assignment/TalentMatrix/data/dataset/trainResumes"
path_to_test_resume = "/home/kiran/assignment/TalentMatrix/data/dataset/testResumes"
path_to_train_csv = "/home/kiran/assignment/TalentMatrix/data/dataset/train.csv"
path_to_test_csv = "/home/kiran/assignment/TalentMatrix/data/dataset/test.csv"

md = MarkItDown()

def doc_markdown(file_path):
    reader = DOC_READER(md)
    for file in os.listdir(file_path):
        text = reader.doc_markdown(f"{file_path}/{file}")
        print(text)


if __name__ == "__main__":
    doc_markdown(path_to_jd)