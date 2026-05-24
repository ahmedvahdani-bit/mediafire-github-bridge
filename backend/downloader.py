import requests
import re
from bs4 import BeautifulSoup
import os
from .utils import logger

class MediaFireDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        })

    def extract_direct_link(self, url: str) -> str:
        """Scrapes the MediaFire page to find the actual direct download link."""
        logger.info(f"Extracting direct link from: {url}")
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            download_btn = soup.find('a', id='downloadButton')
            
            if download_btn and 'href' in download_btn.attrs:
                direct_link = download_btn['href']
                logger.info(f"Direct link found: {direct_link}")
                return direct_link
            
            # Fallback regex if HTML structure changes
            match = re.search(r'href="(https://download\d+\.mediafire\.com/[^"]+)"', response.text)
            if match:
                return match.group(1)
                
            raise ValueError("Could not locate direct download link.")
            
        except Exception as e:
            logger.error(f"Failed to extract direct link: {e}")
            raise

    def download_file(self, url: str, output_path: str) -> str:
        """Downloads the file robustly using streaming."""
        direct_link = self.extract_direct_link(url)
        
        logger.info(f"Starting download to {output_path}")
        try:
            with self.session.get(direct_link, stream=True, timeout=20) as r:
                r.raise_for_status()
                with open(output_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            logger.info("Download completed successfully.")
            return output_path
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise
