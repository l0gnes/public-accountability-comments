from dataclasses import dataclass
from typing import List

@dataclass
class CSVFileMetadata(object):

    channel_handle : str
    video_ids : List[str]

    @property
    def video_id_count(self):
        return len(self.video_ids)

    @property
    def has_videos(self) -> bool:
        return self.video_id_count > 0

    def __repr__(self) -> str:
        return f"<CSVFileMetadata {self.channel_handle=} {self.video_id_count=}>"