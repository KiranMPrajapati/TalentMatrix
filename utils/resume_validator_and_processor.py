import re
import json
from pydantic import ValidationError


# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from .validator import Resume


class ResumeProcessor:
    def __init__(self, llm, max_retries = 3):
        self.llm = llm  
        self.count = 0
        self.retry = False
        self.max_retries = max_retries

    def validate_and_process(self, resume_text, data):
        """
        Validate the data using the Resume model. If validation fails, rerun the LLM for invalid sections.
        """
        try:
            print(data)
            if isinstance(data, re.Match):
                if data.groups():
                    data = data.group(1)  # Group 1 contains the matched value
                else:
                    data = data.group()  # No groups, return full match
                if isinstance(data, tuple):
                    data = data[0]
                data = json.loads(data)
                # print(json.dumps(parsed_json, indent=4))
            print(data)
            resume = Resume(**data)
            print("Validation passed.")
            return resume.dict(), False 
        except ValidationError as e:
            print("Validation failed. Errors detected.")
            error_sections = self.parse_validation_errors(e, data)
            
            reprocessed_data = self.rerun_llm_for_errors(error_sections)

            merged_data = self.merge_data(data, reprocessed_data)
            self.count += 1

            if self.count >= self.max_retries:
                return f"The resume is not complete and rejected. Following issue occured: \n {e}", False
            return self.validate_and_process(resume_text, merged_data), False

    def parse_validation_errors(self, error, original_data):
        """
        Extract invalid sections from validation errors.
        """
        invalid_sections = {}
        for err in error.errors():
            field = err['loc'][0]
            if field not in original_data:
                continue
            if field not in invalid_sections:
                invalid_sections[field] = original_data[field]
        return invalid_sections

    def rerun_llm_for_errors(self, invalid_sections):
        """
        Rerun the LLM for invalid sections to regenerate their data.
        """
        reprocessed_data = {}
        for section, content in invalid_sections.items():
            # Convert invalid section back to text for the LLM
            text_input = f"Invalid section detected: {section}. Data: {content}"
            print(f"Reprocessing {section}...")
            self.retry = True
            regenerated_output = self.llm(text_input, self.retry)
            # Assuming LLM output is structured correctly, convert it to Python dict
            reprocessed_data[section] = self.parse_llm_output(regenerated_output)
        return reprocessed_data

    def parse_llm_output(self, llm_output):
        """
        Safely parse the LLM output (assuming it's valid JSON format).
        """
        try:
            json_string = llm_output.group()
            return json.loads(json_string)  
        except json.JSONDecodeError:
            print("Error: LLM output is not valid JSON.")
            return {}

    def merge_data(self, original_data, reprocessed_data):
        """
        Merge original data with reprocessed data, replacing invalid sections.
        """
        merged_data = original_data.copy()
        merged_data.update(reprocessed_data)
        return merged_data