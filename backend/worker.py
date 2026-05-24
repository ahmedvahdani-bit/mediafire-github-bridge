import os
import sys
from .utils import logger, ensure_directory, get_env_var
from .downloader import MediaFireDownloader
from .splitter import FileSplitter
from .manifest import create_manifest

def main():
    logger.info("--- Starting GitHub Actions Automation Worker ---")
    
    # Retrieve dynamic inputs
    mediafire_url = get_env_var("MEDIAFIRE_URL")
    job_id = get_env_var("JOB_ID")
    
    # Setup directories
    job_dir = os.path.join("data", "jobs", job_id)
    ensure_directory(job_dir)
    
    temp_dir = os.path.join("data", "temp")
    ensure_directory(temp_dir)
    
    # Extract intended filename (basic approximation from URL for temp storage)
    temp_filename = "downloaded_file.tmp"
    temp_filepath = os.path.join(temp_dir, temp_filename)
    
    try:
        # Phase 1: Download
        logger.info(f"Initiating download for Job ID: {job_id}")
        downloader = MediaFireDownloader()
        downloader.download_file(mediafire_url, temp_filepath)
        
        # Determine actual file extension/name (For simplicity, wrapping in standard names, 
        # normally you'd parse headers for 'Content-Disposition')
        original_name = "archive.zip" # Default generic name
        final_temp_path = os.path.join(temp_dir, original_name)
        os.rename(temp_filepath, final_temp_path)
        
        # Phase 2: Split
        logger.info("Initiating file splitting...")
        splitter = FileSplitter(chunk_size_mb=90)
        chunks = splitter.split(final_temp_path, job_dir)
        
        # Phase 3: Manifest Generation
        logger.info("Generating manifest...")
        create_manifest(job_id, original_name, chunks, job_dir)
        
        logger.info("--- Worker Execution Completed Successfully ---")
        
    except Exception as e:
        logger.error(f"Job failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
