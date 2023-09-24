from typing import (
    Any, TYPE_CHECKING, Literal, Union, List, Generator
)

from objects.PaginatedResults import PaginatedResults
from objects.Comment import Comment
from objects.CommentThread import CommentThread
from math import ceil

from googleapiclient.errors import HttpError

from rich.console import Console

if TYPE_CHECKING:
    from googleapiclient._apis.youtube.v3.resources import YouTubeResource

class CommentPullingModule(object):

    YOUTUBE : "YouTubeResource"
    CONSOLE : Console

    def __init__(self, yt : "YouTubeResource", console : Console) -> None:

        self.YOUTUBE = yt
        self.CONSOLE = console



    def getCommentThreadsFromVideoId(
            self, 
            video_id : str,
            subset_replies : bool,
            *,
            text_format : Literal["html", "plainText"] = "plainText"
        ) -> Union[PaginatedResults[CommentThread], None]:

        _parts = ['snippet']

        if subset_replies: _parts.append('replies')

        req = self.YOUTUBE.commentThreads().list(
            part = ",".join(_parts),
            maxResults = 100,
            videoId = video_id,
            textFormat = text_format
        )

        res = req.execute()

        return PaginatedResults[CommentThread](
            self.YOUTUBE,
            req, res,
            self.YOUTUBE.commentThreads(),
            CommentThread
        )



    def getCommentsFromCommentIds(
            self,
            commentIds : List[str],
            *,
            text_format : Literal['html', 'plainText'] = 'plainText'
    ) -> Union[List[Comment], None]:
        
        req = self.YOUTUBE.comments().list(
            part = "id,snippet",
            id = ','.join(commentIds),
            textFormat = text_format
        )

        res = req.execute()

        return [
            Comment.construct_from_response(x) for x in res['items']
        ]




    def getTopLevelCommentsFromPaginatedCommentThread(
            self,
            comment_thread : PaginatedResults[CommentThread]
    ) -> List[Comment]:

        # Fetch a list of comment ids
        cids : List[str] = comment_thread.map_to_response(
            lambda n: n.top_level_comment.comment_id)
        
        # max amount of results for this query is 50 ids at a time (sadge)
        p1 : List[Comment] = self.getCommentsFromCommentIds(cids[:50])
        p2 : List[Comment] = self.getCommentsFromCommentIds(cids[50:])

        # I hope this works as intended
        return p1 + p2



    def getCommentsAndRepliesFromPaginatedCommentThread(
            self,
            comment_thread : PaginatedResults[CommentThread]
    ) -> List[Comment]:
        
        # Getting all of the comment ids
        cids = []
        for c in comment_thread.get_wrapped_items():
            
            if c.has_replies:
                cids.extend(
                    map(lambda n: n.comment_id, c.subset_of_replies)
                )

            cids.append(c.top_level_comment.comment_id)
        
        req_count = ceil(len(cids) / 50)
        ret_val : List[Comment] = []

        for i in range(req_count):

            ret_val.extend(
                self.getCommentsFromCommentIds(
                    cids[50 * i : 50 * (i + 1)]
                )
            )

        return ret_val