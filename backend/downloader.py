import requests
import re
import os
import yt_dlp
from .utils import logger

class UniversalDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36"
        })

    def is_mediafire_folder(self, url: str) -> bool:
        return "mediafire.com/folder/" in url

    def resolve_mediafire_folder(self, url: str) -> list:
        """Extracts files from MediaFire API."""
        logger.info(f"Scanning MediaFire folder: {url}")
        try:
            match = re.search(r'/folder/([a-zA-Z0-9]+)', url)
            if not match: return []
            
            folder_key = match.group(1)
            api_url = f"https://www.mediafire.com/api/1.4/folder/get_content.php?folder_key={folder_key}&content_type=files&response_format=json"
            
            response = self.session.get(api_url, timeout=15)
            response.raise_for_status()
            files = response.json().get('response', {}).get('folder_content', {}).get('files', [])
            
            return [f"https://www.mediafire.com/file/{f.get('quickkey')}/{f.get('filename')}" for f in files if f.get('quickkey')]
        except Exception as e:
            logger.error(f"MediaFire API error: {e}")
            return []

    def download_with_ytdlp(self, url: str, quality: str, output_dir: str) -> str:
        """Handles YouTube, Generic Direct Links using yt-dlp and injects cookies if available."""
        logger.info(f"Using yt-dlp to process: {url}")
        
        format_string = 'bestvideo+bestaudio/best'
        if quality == '1080p':
            format_string = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
        elif quality == '720p':
            format_string = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
        elif quality == 'audio':
            format_string = 'bestaudio/best'

        ydl_opts = {
            'format': format_string,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
            'nocheckcertificate': True
        }

        # Handle YouTube Cookies from GitHub Secrets
        cookies_content = os.environ.get("YT_COOKIES", "")
        if cookies_content and cookies_content.strip():
            cookies_path = os.path.join(output_dir, "cookies.txt")
            try:
                with open(cookies_path, "w", encoding="utf-8") as f:
                    f.write(cookies_content)
                ydl_opts['cookiefile'] = cookies_path
                logger.info("✅ YouTube cookies loaded successfully from GitHub Secrets.")
            except Exception as e:
                logger.error(f"Failed to write cookies file: {e}")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                downloaded_file_path = ydl.prepare_filename(info_dict)
                
                base, ext = os.path.splitext(downloaded_file_path)
                expected_merged_path = base + '.' + ydl_opts.get('merge_output_format', 'mp4')
                
                if os.path.exists(expected_merged_path):
                    return expected_merged_path
                return downloaded_file_path
                
        except Exception as e:
            logger.error(f"yt-dlp failed: {e}")
            raise
