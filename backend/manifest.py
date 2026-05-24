import json
import os
import datetime
from .utils import logger

def create_manifest(job_id: str, original_filename: str, chunks: list, output_dir: str):
    """Generates a JSON manifest file for easy reconstruction."""
    manifest_data = {
        "job_id": job_id,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "original_filename": original_filename,
        "total_chunks": len(chunks),
        "chunks": chunks
    }
    
    manifest_path = os.path.join(output_dir, "manifest.json")
    try:
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=4)
        logger.info(f"Manifest created at {manifest_path}")
    except Exception as e:
        logger.error(f"Failed to create manifest: {e}")
