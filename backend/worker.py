import os
import sys
from .utils import logger, ensure_directory, get_env_var
from .downloader import UniversalDownloader
from .splitter import FileSplitter
from .manifest import create_master_manifest

def main():
    logger.info("--- Starting Universal Downloader V2 ---")
    
    target_url = get_env_var("TARGET_URL")
    job_id = get_env_var("JOB_ID")
    quality = get_env_var("QUALITY", "best")
    
    job_dir = os.path.join("data", "jobs", job_id)
    temp_dir = os.path.join("data", "temp")
    ensure_directory(job_dir)
    ensure_directory(temp_dir)
    
    downloader = UniversalDownloader()
    splitter = FileSplitter(chunk_size_mb=90)
    all_files_metadata = []
    
    try:
        # Determine Flow based on URL type
        urls_to_process = []
        if downloader.is_mediafire_folder(target_url):
            logger.info("MediaFire Folder flow selected.")
            urls_to_process = downloader.resolve_mediafire_folder(target_url)
        else:
            logger.info("Single Link / YouTube flow selected.")
            urls_to_process = [target_url]

        if not urls_to_process:
            logger.error("No extractable links found.")
            sys.exit(1)

        for index, url in enumerate(urls_to_process, start=1):
            logger.info(f"\n>>> Processing Link {index}/{len(urls_to_process)} <<<")
            
            try:
                # Download using the universal yt-dlp engine
                downloaded_file_path = downloader.download_with_ytdlp(url, quality, temp_dir)
                
                original_name = os.path.basename(downloaded_file_path)
                file_base_name = os.path.splitext(original_name)[0]
                
                file_specific_dir = os.path.join(job_dir, file_base_name)
                
                # Resume/Skip Logic
                if os.path.exists(file_specific_dir) and os.listdir(file_specific_dir):
                    logger.info(f"⏭️ SKIPPING: Folder '{file_base_name}' already exists.")
                    existing_chunks = sorted([f for f in os.listdir(file_specific_dir) if os.path.isfile(os.path.join(file_specific_dir, f))])
                    all_files_metadata.append({
                        "original_filename": original_name,
                        "folder_name": file_base_name,
                        "total_chunks": len(existing_chunks),
                        "chunks": [f"{file_base_name}/{c}" for c in existing_chunks]
                    })
                    if os.path.exists(downloaded_file_path):
                        os.remove(downloaded_file_path) # Cleanup temp
                    continue
                
                ensure_directory(file_specific_dir)
                
                # Split Logic
                logger.info(f"Splitting {original_name} into {file_specific_dir}")
                chunks = splitter.split(downloaded_file_path, file_specific_dir)
                
                all_files_metadata.append({
                    "original_filename": original_name,
                    "folder_name": file_base_name,
                    "total_chunks": len(chunks),
                    "chunks": [f"{file_base_name}/{c}" for c in chunks]
                })
                
            except Exception as item_err:
                logger.error(f"Failed to process item {url}: {item_err}")
                continue # Continue with the next file even if one fails

        # Master Manifest Generation
        logger.info("\nGenerating master manifest...")
        create_master_manifest(job_id, all_files_metadata, job_dir)
        logger.info("--- V2 Worker Execution Completed ---")
        
    except Exception as e:
        logger.error(f"Critical Job failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
