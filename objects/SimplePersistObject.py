from dataclasses import dataclass, asdict, field
from os import PathLike
from typing import TYPE_CHECKING, MutableSet

if TYPE_CHECKING:
    from objects.CSVFileMetadata import CSVFileMetadata

@dataclass
class SimplePersistObject(object):

    channel_handle : str
    video_id : str

    def to_dict(self) -> dict:
        return {
            "channel_handle" : self.channel_handle,
            "video_id" : self.video_id
        }
    
    def push_video_id(self, v : str):
        self.video_id = v

    def push_channel(self, c : "CSVFileMetadata"):
        self.channel_handle = c.channel_handle

    @property
    def is_empty(self) -> bool:
        return self.channel_handle == '' and self.video_id == ''