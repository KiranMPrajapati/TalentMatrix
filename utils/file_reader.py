import json


def json_reader(file_path="prompt_tuner/json_response_sample_schema.json"):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            print("JSON file loaded successfully!")
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


def text_reader(file_path="prompt_tuner/resume_sample_text.txt"):
    try:
        with open(file_path, 'r') as file:
            normalized_lines = [' '.join(line.split()) for line in file]  
            normalized_content = ' '.join(normalized_lines)  
        return normalized_content
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

