import os
import re
import time
import yt_dlp
from typing import Optional, Tuple
from config import TEMP_DIR, MAX_FILE_SIZE_FREE, MAX_FILE_SIZE_PREMIUM

class VideoDownloader:
    @staticmethod
    def get_platform(url: str) -> Optional[str]:
        """Determine the platform from URL."""
        if "tiktok.com" in url:
            return "tiktok"
        elif "instagram.com" in url:
            return "instagram"
        return None

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid for supported platforms."""
        return bool(re.search(r'(tiktok\.com|instagram\.com)', url))

    @staticmethod
    def get_download_options(is_premium: bool, platform: str) -> dict:
        """Get download options based on user status and platform."""
        max_size = MAX_FILE_SIZE_PREMIUM if is_premium else MAX_FILE_SIZE_FREE
        
        if platform == "instagram":
            return {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'quiet': True,
                'noplaylist': True
            }
        else:  # TikTok and others
            if is_premium:
                return {
                    'format': 'best',
                    'quiet': True,
                    'noplaylist': True,
                    'extractor_args': {
                        'tiktok': {
                            'api_hostname': 'api16-normal-c-useast1a.tiktokv.com',
                            'app_version': '20.2.1',
                            'device_id': '7168534261740988934',
                            'channel': 'googleplay',
                            'mcc_mnc': '310260',
                            'os_version': '10',
                            'version_code': '200201',
                            'device_type': 'Pixel 4',
                            'language': 'en',
                            'resolution': '1080*1920',
                            'openudid': 'a1b2c3d4e5f6g7h8',
                            'sys_region': 'US',
                            'os_api': '29',
                            'timezone_name': 'America/New_York',
                            'residence': 'US',
                            'app_language': 'en',
                            'ac2_wifi': '0',
                            'dpi': '420',
                            'carrier_region': 'US',
                            'ac': 'wifi',
                            'app_name': 'trill',
                            'device_platform': 'android',
                            'build_number': '10.2.1',
                            'version_name': '10.2.1',
                            'timezone_offset': '-14400',
                            'channel': 'googleplay',
                            'mcc_mnc': '310260',
                            'is_my_cn': '0',
                            'aid': '1340',
                            'ssmix': 'a',
                            'as': 'a1qwert123',
                            'cp': 'androide1',
                            'mas': '0123456789abcdef'
                        }
                    }
                }
            else:
                return {
                    'format': f'best[filesize<{max_size}M]',
                    'quiet': True,
                    'noplaylist': True,
                    'extractor_args': {
                        'tiktok': {
                            'api_hostname': 'api16-normal-c-useast1a.tiktokv.com',
                            'app_version': '20.2.1',
                            'device_id': '7168534261740988934',
                            'channel': 'googleplay',
                            'mcc_mnc': '310260',
                            'os_version': '10',
                            'version_code': '200201',
                            'device_type': 'Pixel 4',
                            'language': 'en',
                            'resolution': '1080*1920',
                            'openudid': 'a1b2c3d4e5f6g7h8',
                            'sys_region': 'US',
                            'os_api': '29',
                            'timezone_name': 'America/New_York',
                            'residence': 'US',
                            'app_language': 'en',
                            'ac2_wifi': '0',
                            'dpi': '420',
                            'carrier_region': 'US',
                            'ac': 'wifi',
                            'app_name': 'trill',
                            'device_platform': 'android',
                            'build_number': '10.2.1',
                            'version_name': '10.2.1',
                            'timezone_offset': '-14400',
                            'channel': 'googleplay',
                            'mcc_mnc': '310260',
                            'is_my_cn': '0',
                            'aid': '1340',
                            'ssmix': 'a',
                            'as': 'a1qwert123',
                            'cp': 'androide1',
                            'mas': '0123456789abcdef'
                        }
                    }
                }

    @staticmethod
    async def download_video(url: str, user_id: str, is_premium: bool) -> Tuple[bool, str, Optional[str]]:
        """Download video from URL."""
        platform = VideoDownloader.get_platform(url)
        if not platform:
            return False, "Unsupported platform", None

        output_file = f"{TEMP_DIR}/{user_id}_{int(time.time())}.mp4"
        
        try:
            ydl_opts = VideoDownloader.get_download_options(is_premium, platform)
            ydl_opts['outtmpl'] = output_file
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return True, output_file, platform
            else:
                return False, "Download failed - empty file", None
                
        except Exception as e:
            error_msg = str(e)
            
            # Try alternative download method for Instagram if first fails
            if platform == "instagram" and "Requested format is not available" in error_msg:
                try:
                    alternative_opts = {
                        'format': 'best',
                        'outtmpl': output_file,
                        'quiet': True,
                        'noplaylist': True
                    }
                    with yt_dlp.YoutubeDL(alternative_opts) as ydl:
                        ydl.download([url])
                    
                    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                        return True, output_file, platform
                except Exception as alt_e:
                    return False, f"Alternative download failed: {alt_e}", None
            
            return False, f"Download error: {error_msg}", None

    @staticmethod
    def cleanup_file(file_path: str) -> None:
        """Clean up downloaded file."""
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing file {file_path}: {e}") 
