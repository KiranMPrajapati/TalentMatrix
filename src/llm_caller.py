import re
import math
import json
import torch

from transformers import AutoModelForCausalLM, AutoTokenizer


class LLM:
    def __init__(self, model_name="Qwen/Qwen2.5-7B-Instruct", max_chunk_size=1024):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_chunk_size = max_chunk_size
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.model = torch.compile(self.model)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.summary_text = ""

    def chunk_text(self, text):
        """
        Splits text into smaller chunks that fit within the model's maximum input size.
        """
        tokens = self.tokenizer(text, return_tensors="pt", truncation=False)["input_ids"][0]
        total_chunks = math.ceil(tokens.size(0) / self.max_chunk_size)
        chunks = [tokens[i * self.max_chunk_size:(i + 1) * self.max_chunk_size] for i in range(total_chunks)]
        return chunks

    def create_summarizer_prompt(self):
        SYSTEM_PROMPT = """You are a highly intelligent AI designed to generate concise, accurate, and clear summaries. 
        Your task is to analyze the given text and produce a summary that preserves its core ideas and essential information. 
        Ensure that the summary is easy to understand, brief, and free from unnecessary details. Focus on clarity and relevance, maintaining the original meaning and context of the content provided."""

        schema_description = """Summarize the following text in a concise and clear manner, preserving its key points, main ideas, and important details"""

        return SYSTEM_PROMPT, schema_description

    def create_json_extractor_prompt(self):
        SYSTEM_PROMPT = """You are a highly intelligent AI designed to extract structured information from resumes. 
        Your goal is to analyze a given resume text and return the extracted details in the following JSON schema format."""

        schema_description = """Here is a JSON format:
        {
            "basics": { ... },
            "work": [ ... ],
            "volunteer": [ ... ],
            "education": [ ... ],
            "awards": [ ... ],
            "certificates": [ ... ],
            "publications": [ ... ],
            "skills": [ ... ],
            "languages": [ ... ],
            "interests": [ ... ],
            "references": [ ... ],
            "projects": [ ... ]
        }
        Your task is to:
        1. Parse the resume text carefully, identifying the relevant sections.
        2. Populate the schema fields with the corresponding information from the resume.
        3. Do not include any field or section in the JSON output if the data for it is not present in the resume.
        4. Preserve the structure of the JSON format for the included data, ensuring proper syntax and completeness.

        When extracting details:
        1. Prioritize accuracy.
        2. Ensure that no empty fields, objects, or arrays are returned.
        3. Omit any ambiguous or irrelevant information entirely from the output.

        You have to output JSON FORMAT only. 
        """

        return SYSTEM_PROMPT, schema_description

    def generate_response(self, resume_text, system_prompt, schema_description):
        chunks = self.chunk_text(resume_text)

        complete_response = ""
        for chunk in chunks:
            chunk_text = self.tokenizer.decode(chunk, skip_special_tokens=True)
            prompt = f"{schema_description}\n\nResume Chunk:\n{chunk_text}"

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            print('here1')
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            print('here2')
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            print('here3')

            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512,
                num_beams=1
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            print('here4')

            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            complete_response += response.strip() + "\n"
        return complete_response
        

    def __call__(self, resume_text, retry=False):
        if not retry:
            system_prompt, schema_description = self.create_summarizer_prompt()
            self.summary_text = self.generate_response(resume_text, system_prompt, schema_description)
            print(self.summary_text)
        system_prompt, schema_description = self.create_json_extractor_prompt()
        complete_response = self.generate_response(self.summary_text, system_prompt, schema_description)
        print(complete_response)

        # Extract the JSON structure from the input string
        json_match = re.search(r'```json\n(.*?)\n```', complete_response, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
            try:
                # Parse the JSON structure
                data = json.loads(json_string)
                # print(json.dumps(parsed_json, indent=4))
                return data
            except:
                print("Validation failed. Errors detected.")        