from dataclasses import dataclass, asdict
from objects.Comment import Comment 
from typing import Optional, List

@dataclass
class CommentThread(object):

    comment_thread_id : str
    channel_id : str
    video_id : str
    top_level_comment : Comment
    can_reply : bool
    total_reply_count : int
    is_public : bool

    subset_of_replies : Optional[List[Comment]]

    @property
    def has_replies(self) -> bool:
        return len(self.subset_of_replies) > 0

    @classmethod
    def construct_from_response(cls, d : dict) -> "CommentThread":
        
        replies = []

        if d.get('replies', None):
            if d['replies'].get('comments', None):
                replies = d['replies']['comments']

        x = cls(
            comment_thread_id = d['id'],
            channel_id = d['snippet']['channelId'],
            video_id = d['snippet']['videoId'],
            top_level_comment = Comment.construct_from_response(d['snippet']['topLevelComment']),
            can_reply = d['snippet']['canReply'],
            total_reply_count = d['snippet']['totalReplyCount'],
            is_public = d['snippet']['isPublic'],

            subset_of_replies = [
                Comment.construct_from_response(reply) for reply in replies
            ]
        )

        return x