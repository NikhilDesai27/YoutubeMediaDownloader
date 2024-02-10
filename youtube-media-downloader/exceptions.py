from typing import Optional
class InvalidYoutubeURL(Exception):
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(self.error_string)

    @property
    def error_string(self):
        return f"URL: {self.url} does not point to a valid Youtube Media"
    
class MediaOptionsUnavailable(Exception):
    def __init__(self, url: str, wrapped_exception: Optional[Exception] = None) -> None:
        self.url = url
        self.wrapped_exception = wrapped_exception
        if not self.wrapped_exception:
            self.wrapped_exception = InvalidYoutubeURL(url)
        super().__init__(self.error_string)

    @property
    def error_string(self):
        return f"Cannot get media options for content at {self.url} because, {self.wrapped_exception}"