import pymupdf4llm

class DOC_READER:
    def __init__(self, md, type="markitdown"):
        self.md = md 
        self.type = type

    def doc_markdown(self, filename: str) -> str:
        if isinstance(filename, str):
            if self.type == "pymupdf4llm":
                return pymupdf4llm.to_markdown(filename)
            elif self.type == "markitdown":
                return  self.md.convert(filename).text_content
            else:
                raise ValueError("Such reader does not exist in the system")
        else:
            raise ValueError("Input must be a string")
    
