from os import PathLike
import sqlite3
from typing import (
    List, TYPE_CHECKING
)

if TYPE_CHECKING:
    from objects.Comment import Comment

class DatabaseHandler(object):

    OUT_PATH : PathLike
    CONNECTION : sqlite3.Connection

    def __init__(
            self, 
            out_path : PathLike = "./out.db") -> None:
        
        self.OUT_PATH = out_path
        self.connection_init()

    def connection_init(self) -> None:
        
        self.CONNECTION = sqlite3.connect(self.OUT_PATH)

        # Weirdest way to do a context manager but ok
        with self.CONNECTION:

            with open('./schema.sqlite', 'r') as schema:

                self.CONNECTION.executescript(
                    schema.read()
                )


    def push_comments(
            self,
            comments : List["Comment"],
            *,
            override_video : bool = False,
            video_id : str = None) -> None:
        
        if override_video:
            for c in comments:
                if not c.comment_parent: # Only if the comment doesn't have a parent comment
                    c.comment_video_id = video_id # Override the video_id

        with self.CONNECTION:
            self.CONNECTION.executemany(
                """
                INSERT OR REPLACE INTO comments
                (id, author_name, author_avatar, author_url, author_id, channel_id, video_id, content, parent, can_like, like_count, publish_time, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """.strip(),
                map(lambda n: n.to_array(), comments)
            )

    def cleanup(self) -> None:

        self.CONNECTION.close()