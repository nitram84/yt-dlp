from .common import InfoExtractor
from ..utils import ExtractorError
import re

class WedoTVIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?wedotv\.com/(?:[a-z]{2}-[a-z]{2}/)?(?P<id>[^/?#]+)'

    _TESTS = [{
        'url': 'https://www.wedotv.com/de-de/you-stupid-man',
        'info_dict': {
            'display_id': 'you-stupid-man',
        },
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        video_id = self._search_regex(
            r'data-video-id="(\d+)"', 
            webpage, 'internal video ID', default=None)

        if not video_id:
            raise ExtractorError('Video-ID not found.', expected=True)

        video_data = self._download_json(
            f'https://www.wedotv.com/api/player.get_video.php?video_id={video_id}',
            video_id,
            note='Fetch video metadata',
            errnote='Failed to fetch metadata'
        )

        m3u8_url = video_data.get('video_source')
        if not m3u8_url:
            raise ExtractorError('No stream found', expected=True)

        title = video_data.get('title')

        formats = self._extract_m3u8_formats(
            m3u8_url, video_id, 'mp4', entry_protocol='m3u8_native', m3u8_id='hls')

        return {
            'id': video_id,
            'display_id': display_id,
            'title': title,
            'formats': formats,
            'description': self._og_search_description(webpage),
            'thumbnail': self._og_search_thumbnail(webpage),
        }
