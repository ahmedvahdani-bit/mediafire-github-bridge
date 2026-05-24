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

    def resolve_urls(self, url: str) -> list:
        """Checks if URL is a folder and extracts all file links using MediaFire API."""
        if "/folder/" in url:
            logger.info(f"Folder detected. Scanning for files in: {url}")
            try:
                # Extract folder key from the URL
                match = re.search(r'/folder/([a-zA-Z0-9]+)', url)
                if not match:
                    logger.error("Could not extract folder key from URL.")
                    return []
                
                folder_key = match.group(1)
                logger.info(f"Extracted folder key: {folder_key}")
                
                # Call MediaFire's internal API to get folder contents dynamically
                api_url = f"https://www.mediafire.com/api/1.4/folder/get_content.php?folder_key={folder_key}&content_type=files&response_format=json"
                
                response = self.session.get(api_url, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                # Parse JSON response
                files = data.get('response', {}).get('folder_content', {}).get('files', [])
                
                links = []
                for f in files:
                    quickkey = f.get('quickkey')
                    filename = f.get('filename')
                    if quickkey:
                        # Construct the standard MediaFire file URL
                        file_link = f"https://www.mediafire.com/file/{quickkey}/{filename}"
                        links.append(file_link)
                
                if not links:
                    logger.warning("No file links found in the folder via API.")
                else:
                    logger.info(f"Found {len(links)} unique files in the folder.")
                
                return links
            except Exception as e:
                logger.error(f"Failed to scan folder via API: {e}")
                raise
        else:
            return [url]

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
                logger.info("Direct link found successfully.")
                return direct_link
            
            # Fallback regex if HTML structure changes
            match = re.search(r'href="(https://download\d+\.mediafire\.com/[^"]+)"', response.text)
            if match:
                logger.info("Direct link found via fallback regex.")
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
