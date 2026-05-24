import json
import os
import datetime
from .utils import logger

def create_master_manifest(job_id: str, all_files_data: list, output_dir: str):
    """Generates a single JSON manifest file containing metadata for all files in the job."""
    manifest_data = {
        "job_id": job_id,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "total_files_processed": len(all_files_data),
        "files": all_files_data
    }
    
    manifest_path = os.path.join(output_dir, "master_manifest.json")
    try:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=4, ensure_ascii=False)
        logger.info(f"Master manifest created at {manifest_path}")
    except Exception as e:
        logger.error(f"Failed to create master manifest: {e}")
