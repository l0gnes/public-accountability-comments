from typing import TYPE_CHECKING, TypeVar, Literal, Optional
from objects.SimplePersistObject import SimplePersistObject
from os import PathLike
from os.path import exists
import json

if TYPE_CHECKING:
    from modules.CommentPullingModule import CommentPullingModule
    from googleapiclient._apis.youtube.v3.resources import YouTubeResource
    from objects.PaginatedResults import PaginatedResults
    from objects.CSVFileMetadata import CSVFileMetadata
    
from rich.console import Console

T = TypeVar("T")

class PersistHandler(object):

    SAVED_STATE : SimplePersistObject
    STATE_RESUME_COMPLETE : bool

    CONSOLE : Console

    def __init__(self, console) -> None:

        self.CONSOLE = console

        self.STATE_RESUME_COMPLETE = False

        v = self.pull_state_from_file()

        if v:
            self.CONSOLE.log(
                ":monkey: [cyan bold] State file found! loading state from previous session."
            )
        else:
            self.CONSOLE.log(
                ":wrench: [cyan bold] No state file found! Starting from scratch..."
            )

        
        

    def push_state_to_file(
            self
    ) -> None:
        
        with open('./state.json', 'w+') as state_file:
            json.dump(
                self.SAVED_STATE.to_dict(), state_file
            )



    # Returns `True` if a state was pulled
    def pull_state_from_file(
            self,
    ) -> bool:
        
        if not exists('./state.json'):
            self.SAVED_STATE = SimplePersistObject('', '')
            return False
        
        with open('./state.json', 'r') as state_file:
            JSON_DATA = json.load( state_file )

        self.SAVED_STATE = SimplePersistObject( **JSON_DATA )


        return True
    


    def satisfies_state_check(
            self,
            *,
            channel : Optional["CSVFileMetadata"] = None,
            video_id : Optional[str] = None,
            passthrough_on_resumed : bool = True
        ) -> bool:
            
            if passthrough_on_resumed and self.STATE_RESUME_COMPLETE:
                return True

            if (channel == None and video_id == None) or (channel and video_id):
                raise ValueError("State checks support (and require) only one of kwargs: `channel` or `video_id`")
            
            if channel is not None:
                
                return self.SAVED_STATE.channel_handle == channel.channel_handle or self.SAVED_STATE.channel_handle == ''

            if video_id is not None:

                return self.SAVED_STATE.video_id == video_id or self.SAVED_STATE.video_id == ''