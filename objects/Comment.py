from dataclasses import dataclass, asdict

@dataclass
class Comment(object):

    comment_id : str
    comment_author_name : str
    comment_author_avatar : str
    comment_author_url : str
    comment_author_id : str
    comment_channel_id : str
    comment_video_id : str
    comment_text_display : str
    comment_parent : str
    comment_can_like : bool
    comment_likes : int
    comment_publish_time : str
    comment_update_time : str

    @classmethod
    def construct_from_response(cls, response : dict) -> "Comment":
        
        # Deleted channels sometimes omit their channel ids.
        # We can still pull their comment data however.
        if not response['snippet'].get('authorChannelId', False):
            response['snippet']['authorChannelId'] = {'value' : ''}

        x = cls(
            comment_id = response['id'],
            comment_author_name = response['snippet']['authorDisplayName'],
            comment_author_avatar = response['snippet']['authorProfileImageUrl'],
            comment_author_url = response['snippet']['authorChannelUrl'],
            comment_author_id = response['snippet']['authorChannelId']['value'],
            comment_channel_id = response['snippet']['channelId'],
            comment_video_id = response['snippet'].get('videoId', None),
            comment_text_display = response['snippet']['textDisplay'],
            comment_parent = response['snippet'].get('parentId', None),
            comment_can_like = response['snippet']['canRate'],
            comment_likes = response['snippet'].get('likeCount', -1),
            comment_publish_time = response['snippet']['publishedAt'],
            comment_update_time = response['snippet']['updatedAt']
        )

        return x
    
    def to_array(self) -> list:
        return [
            self.comment_id,
            self.comment_author_name,
            self.comment_author_avatar,
            self.comment_author_url,
            self.comment_author_id,
            self.comment_channel_id,
            self.comment_video_id,
            self.comment_text_display,
            self.comment_parent,
            self.comment_can_like,
            self.comment_likes,
            self.comment_publish_time,
            self.comment_update_time
        ]