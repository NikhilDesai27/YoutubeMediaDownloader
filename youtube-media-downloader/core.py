from exceptions import InvalidYoutubeURL, MediaOptionsUnavailable
from interfaces import YoutubeMedia
from typing import Optional, Collection
from pathlib import Path
from pytube import YouTube, Stream
from pytube.exceptions import VideoUnavailable

class PytubeStreamAsYoutubeMedia:

    def __init__(self, stream: Stream):
        self.stream = stream

    def id(self) -> str:
        return str(self.stream.itag)
    
    def media_type(self) -> str:
        if self.stream.is_progressive:
            return "Audio-and-Video"
        if self.includes_audio_track:
            return "Audio"
        return "Video"
    
    def file_type(self) -> str:
        return self.stream.subtype
    
    def resolution(self) -> Optional[str]:
        if self.media_type() == "Audio":
            return None
        return self.stream.resolution
    
    def audio_bit_rate(self) -> Optional[str]:
        if self.media_type() == "Video":
            return None
        return self.stream.abr
    
    def download(self, filename_to_save_as: str) -> str:
        return self.stream.download(output_path = filename_to_save_as)
    
class PytubeBasedCoreComponent:

    def __init__(self) -> None:
        pass

    def media_options_for(self, url: str) -> Collection[YoutubeMedia]:
        try:
            yt = YouTube(url)
        except VideoUnavailable as e:
            raise MediaOptionsUnavailable(url, e)
        return self.__to_youtube_media(yt.fmt_streams)

    def __to_youtube_media(self, streams: Collection[Stream]) -> Collection[YoutubeMedia]:
        return [PytubeStreamAsYoutubeMedia(stream) for stream in streams]