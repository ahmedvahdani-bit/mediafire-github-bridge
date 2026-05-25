import os
import shutil
from .utils import logger

class FileSplitter:
    def __init__(self, chunk_size_mb: int = 90):
        # Calculate exactly 90MB in bytes
        self.chunk_size_bytes = chunk_size_mb * 1024 * 1024

    def split(self, file_path: str, output_dir: str) -> list:
        """Splits a large file or moves a small file directly to the output directory."""
        logger.info(f"Processing file: {file_path}")
        
        file_size = os.path.getsize(file_path)
        base_name = os.path.basename(file_path)
        
        # If file is smaller than 90MB, just move it to the output folder
        if file_size <= self.chunk_size_bytes:
            logger.info("File is smaller than chunk size. Moving directly to output directory.")
            dest_path = os.path.join(output_dir, base_name)
            shutil.move(file_path, dest_path)
            return [base_name]
            
        chunks = []
        with open(file_path, 'rb') as f:
            chunk_num = 1
            while True:
                chunk_data = f.read(self.chunk_size_bytes)
                if not chunk_data:
                    break
                    
                chunk_filename = f"{base_name}.part{chunk_num:03d}"
                chunk_path = os.path.join(output_dir, chunk_filename)
                
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                    
                chunks.append(chunk_filename)
                logger.info(f"Created chunk: {chunk_filename}")
                chunk_num += 1
                
        # Remove original temp file after successful split
        os.remove(file_path)
        
        return chunks
