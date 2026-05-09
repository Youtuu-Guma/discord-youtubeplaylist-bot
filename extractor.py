import re

class YouTubeLinkExtractor:
    PATTERN = re.compile(r'(?:youtu\.be\/|v=| \/shorts\/| \/live\/| \/)([0-9A-Za-z_-]{11})(?=[%#?&]|$)')

    @staticmethod
    def extract_video_ids(text: str):
        if not text: return []
        matches = YouTubeLinkExtractor.PATTERN.findall(text)
        return list(dict.fromkeys(matches))