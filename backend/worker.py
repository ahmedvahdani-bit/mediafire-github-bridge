import os
import sys
import re
from urllib.parse import unquote
from .utils import logger, ensure_directory, get_env_var
from .downloader import MediaFireDownloader
from .splitter import FileSplitter
from .manifest import create_master_manifest

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
    
    try:
        downloader = MediaFireDownloader()
        
        # Phase 1: Resolve URLs (Supports both single files and folders)
        logger.info(f"Analyzing Target URL: {mediafire_url}")
        file_urls = downloader.resolve_urls(mediafire_url)
        
        if not file_urls:
            logger.error("No valid files found to download. Exiting.")
            sys.exit(1)
            
        splitter = FileSplitter(chunk_size_mb=90)
        all_files_metadata = []
        
        # Loop through each found file
        for index, file_url in enumerate(file_urls, start=1):
            logger.info(f"\n>>> Processing File {index} of {len(file_urls)} <<<")
            logger.info(f"Target Link: {file_url}")
            
            # Extract original filename from the MediaFire URL
            filename_match = re.search(r'/file/[^/]+/([^/]+)', file_url)
            if filename_match:
                original_name = unquote(filename_match.group(1))
                # Clean invalid characters from filename
                original_name = re.sub(r'[\\/*?:"<>|]', "", original_name)
            else:
                original_name = f"downloaded_file_{index}.bin"
                
            logger.info(f"Extracted Filename: {original_name}")
            
            # Create a specific sub-directory for this exact file (removing extension for clean folder name)
            file_base_name = os.path.splitext(original_name)[0]
            if not file_base_name:
                file_base_name = f"file_{index}"
                
            file_specific_dir = os.path.join(job_dir, file_base_name)
            ensure_directory(file_specific_dir)
            
            temp_filepath = os.path.join(temp_dir, f"temp_{index}.tmp")
            
            # Phase 2: Download
            downloader.download_file(file_url, temp_filepath)
            
            # Rename temp file to original name for accurate splitting
            final_temp_path = os.path.join(temp_dir, original_name)
            os.rename(temp_filepath, final_temp_path)
            
            # Phase 3: Split into the specific sub-directory
            logger.info(f"Splitting {original_name} into folder: {file_specific_dir}")
            chunks = splitter.split(final_temp_path, file_specific_dir)
            
            # Store metadata for this specific file, including its sub-folder path
            all_files_metadata.append({
                "original_filename": original_name,
                "folder_name": file_base_name,
                "total_chunks": len(chunks),
                "chunks": [f"{file_base_name}/{c}" for c in chunks]
            })
        
        # Phase 4: Master Manifest Generation
        logger.info("\nGenerating master manifest for all files...")
        create_master_manifest(job_id, all_files_metadata, job_dir)
        
        logger.info("--- Worker Execution Completed Successfully ---")
        
    except Exception as e:
        logger.error(f"Job failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
