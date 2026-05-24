import os
from .utils import logger

class FileSplitter:
    def __init__(self, chunk_size_mb: int = 90):
        # Calculate exactly 90MB in bytes
        self.chunk_size_bytes = chunk_size_mb * 1024 * 1024

    def split(self, file_path: str, output_dir: str) -> list:
        """Splits a large file into chunks of self.chunk_size_bytes."""
        logger.info(f"Starting split for {file_path} into {self.chunk_size_bytes} byte chunks.")
        
        file_size = os.path.getsize(file_path)
        base_name = os.path.basename(file_path)
        chunks = []
        
        if file_size <= self.chunk_size_bytes:
            logger.info("File is smaller than chunk size. No splitting required.")
            return [file_path]
            
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
                logger.info(f"Created chunk: {chunk_filename} ({len(chunk_data)} bytes)")
                chunk_num += 1
                
        # Optional: Remove original large file to save Action runner space
        os.remove(file_path)
        logger.info("Original file removed from runner after successful split.")
        
        return chunks
