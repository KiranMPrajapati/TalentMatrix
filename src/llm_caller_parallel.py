import os
import math
import torch


from transformers import AutoModelForCausalLM, AutoTokenizer
from concurrent.futures import ProcessPoolExecutor

os.environ["TOKENIZERS_PARALLELISM"] = "false"

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

    def chunk_text(self, text):
        """
        Splits text into smaller chunks that fit within the model's maximum input size.
        """
        tokens = self.tokenizer(text, return_tensors="pt", truncation=False)["input_ids"][0]
        total_chunks = math.ceil(tokens.size(0) / self.max_chunk_size)
        chunks = [tokens[i * self.max_chunk_size:(i + 1) * self.max_chunk_size] for i in range(total_chunks)]
        return chunks

    def create_prompt(self, resume_text):
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
        """

        return SYSTEM_PROMPT, schema_description

    def process_chunk(self, chunk):
        """
        Processes a single chunk by tokenizing, generating, and decoding.
        """
        chunk_text = self.tokenizer.decode(chunk, skip_special_tokens=True)
        system_prompt, schema_description = self.create_prompt(chunk_text)

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
            input_ids=model_inputs.input_ids,
            attention_mask=model_inputs.attention_mask,
            max_new_tokens=512,
            num_beams=1
        )
        return self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

    def __call__(self, resume_text):
        chunks = self.chunk_text(resume_text)

        # Use parallel processing for chunks
        with ProcessPoolExecutor() as executor:
            responses = executor.map(self.process_chunk, chunks)
        
        import pdb; pdb.set_trace()
        return "\n".join(responses)
