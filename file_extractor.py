import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any
import openai

class FileAIExtractor:
    """
    A utility class to upload files, extract details using AI, 
    and write extracted data to output files.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the FileAIExtractor with OpenAI API key.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def read_file(self, file_path: str) -> bytes:
        """
        Read a file and return its content as bytes.
        
        Args:
            file_path: Path to the file to read.
            
        Returns:
            File content as bytes.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, "rb") as f:
            return f.read()
    
    def encode_file_to_base64(self, file_path: str) -> str:
        """
        Encode a file to base64 for API transmission.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Base64 encoded string.
        """
        file_content = self.read_file(file_path)
        return base64.standard_b64encode(file_content).decode("utf-8")
    
    def get_file_mime_type(self, file_path: str) -> str:
        """
        Determine MIME type based on file extension.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            MIME type string.
        """
        extension = Path(file_path).suffix.lower()
        mime_types = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".txt": "text/plain",
            ".json": "application/json",
            ".csv": "text/csv",
        }
        return mime_types.get(extension, "application/octet-stream")
    
    def extract_details_from_file(
        self, 
        file_path: str, 
        extraction_prompt: str,
        model: str = "gpt-4-turbo"
    ) -> str:
        """
        Use AI to extract details from a file.
        
        Args:
            file_path: Path to the file to extract from.
            extraction_prompt: Prompt describing what to extract.
            model: OpenAI model to use.
            
        Returns:
            Extracted details as a string.
        """
        mime_type = self.get_file_mime_type(file_path)
        
        # For text files, read directly
        if mime_type in ["text/plain", "application/json", "text/csv"]:
            with open(file_path, "r") as f:
                file_content = f.read()
            
            message_content = [
                {
                    "type": "text",
                    "text": extraction_prompt + "\n\nFile content:\n" + file_content
                }
            ]
        else:
            # For binary files (images, PDFs), encode to base64
            base64_content = self.encode_file_to_base64(file_path)
            message_content = [
                {
                    "type": "text",
                    "text": extraction_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_content}"
                    }
                }
            ]
        
        response = self.client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ]
        )
        
        return response.content[0].text
    
    def write_to_file(self, content: str, output_path: str, format: str = "txt") -> str:
        """
        Write extracted content to an output file.
        
        Args:
            content: Content to write.
            output_path: Path where to save the output file.
            format: Output format ('txt', 'json', 'csv').
            
        Returns:
            Path to the created file.
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        if format.lower() == "json":
            try:
                # Try to parse as JSON if it's structured data
                data = json.loads(content)
                with open(output_path, "w") as f:
                    json.dump(data, f, indent=2)
            except json.JSONDecodeError:
                # If not valid JSON, wrap in a JSON object
                with open(output_path, "w") as f:
                    json.dump({"extracted_data": content}, f, indent=2)
        else:
            with open(output_path, "w") as f:
                f.write(content)
        
        return output_path
    
    def process_file(
        self,
        input_file_path: str,
        extraction_prompt: str,
        output_file_path: str,
        output_format: str = "txt"
    ) -> Dict[str, Any]:
        """
        Complete pipeline: read file -> extract with AI -> write to output file.
        
        Args:
            input_file_path: Path to input file.
            extraction_prompt: Prompt for AI extraction.
            output_file_path: Path for output file.
            output_format: Output format ('txt', 'json', 'csv').
            
        Returns:
            Dictionary with processing results.
        """
        try:
            print(f"Reading file: {input_file_path}")
            
            print("Extracting details using AI...")
            extracted_data = self.extract_details_from_file(
                input_file_path, 
                extraction_prompt
            )
            
            print("Writing to output file...")
            output_path = self.write_to_file(
                extracted_data, 
                output_file_path, 
                output_format
            )
            
            return {
                "status": "success",
                "input_file": input_file_path,
                "output_file": output_path,
                "extracted_data": extracted_data
            }
        
        except Exception as e:
            return {
                "status": "error",
                "input_file": input_file_path,
                "error": str(e)
            }


# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = FileAIExtractor()
    
    # Example 1: Extract text from an image
    result = extractor.process_file(
        input_file_path="sample_document.pdf",
        extraction_prompt="Extract all text and important details from this document. Format as JSON.",
        output_file_path="output/extracted_data.json",
        output_format="json"
    )
    
    print(f"Processing result: {result}")
