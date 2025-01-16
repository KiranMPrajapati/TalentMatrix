import re
import math
import json
import torch

from transformers import AutoModelForCausalLM, AutoTokenizer

from config import get_logger
from utils.file_reader import json_reader, text_reader

logger = get_logger("MainModule")


class LLM:
    def __init__(self, model_name="Qwen/Qwen2.5-7B-Instruct", max_chunk_size=1024):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_chunk_size = max_chunk_size
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map=self.device
        )
        self.model = torch.compile(self.model)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.summary_text = ""

    def chunk_text(self, text, overlap_size=20):
        """
        Splits text into smaller chunks that fit within the model's maximum input size.
        """
        tokens = self.tokenizer(text, return_tensors="pt", truncation=False)["input_ids"][0]
        total_length = tokens.size(0)
        chunks = []

        # Validate that overlap_size is not larger than max_chunk_size
        if overlap_size >= self.max_chunk_size:
            raise ValueError("overlap_size must be smaller than max_chunk_size to avoid infinite loops.")

        start = 0
        while start < total_length:
            end = min(start + self.max_chunk_size, total_length)
            chunks.append(tokens[start:end])

            start = end - overlap_size

            if end == total_length or start >= total_length:
                break
                
        return chunks


    def create_summarizer_prompt(self):
        SYSTEM_PROMPT = """You are a highly intelligent AI designed to generate concise, accurate, and clear summaries. 
        Your task is to analyze the given text and produce a summary that preserves its core ideas and essential information. 
        Ensure that the summary is easy to understand, brief, and free from unnecessary details. Focus on clarity and relevance, maintaining the original meaning and context of the content provided."""

        schema_description = """Summarize the following text in a concise and clear manner, preserving its key points, main ideas, and important details"""

        return SYSTEM_PROMPT, schema_description

    def create_json_extractor_prompt(self):
        example_text = text_reader()
        example_json = json_reader()
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

        example_schema = f"""
        Here is an example sample:

        RESUME TEXT:
        {example_text}

        EXTRACTED JSON:
        {example_json}
        """

        return SYSTEM_PROMPT, schema_description + example_schema
    
    def count_tokens(self, chunks):
        """
        Calculate token size 
        """
        token_size = 0 
        token_size += sum(chunk.size(0) for chunk in chunks)
        return token_size

    def generate_response(self, resume_text, system_prompt, schema_description):
        """
        Generate LLM response
        """
        chunks = self.chunk_text(resume_text)

        token_size = self.count_tokens(chunks)
        logger.info(f"\nToken size:\n {token_size}")

        complete_response = ""
        for chunk in chunks:
            chunk_text = self.tokenizer.decode(chunk, skip_special_tokens=True)
            prompt = f"{schema_description}\n\nResume Chunk:\n{chunk_text}"

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512,
                num_beams=1
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            complete_response += response.strip() + "\n"
        return complete_response
        

    def __call__(self, resume_text, retry=False):
        if not retry:
            system_prompt, schema_description = self.create_summarizer_prompt()
            self.summary_text = self.generate_response(resume_text, system_prompt, schema_description)
        system_prompt, schema_description = self.create_json_extractor_prompt()
        complete_response = self.generate_response(self.summary_text, system_prompt, schema_description)

        json_match = re.search(r'```json\n(.*?)\n```', complete_response, re.DOTALL)
        return json_match
        # if json_match:
        #     json_string = json_match.group(1)
        #     try:
        #         data = json.loads(json_string)
        #         # print(json.dumps(parsed_json, indent=4))
        #         return data
        #     except:
        #         print("Validation failed. Errors detected.")        