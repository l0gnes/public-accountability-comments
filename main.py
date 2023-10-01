from modules.CSVFileHandler import CSVFileHandler
from modules.CommentPullingModule import CommentPullingModule
from modules.DatabaseHandler import DatabaseHandler
from modules.Persist import PersistHandler

from objects.Comment import Comment
from objects.CommentThread import CommentThread

import googleapiclient.discovery
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from rich.console import Console
from rich.progress import Progress

from typing import (
    Any, TYPE_CHECKING, List
)

if TYPE_CHECKING:
    from googleapiclient._apis.youtube.v3.resources import YouTubeResource


class YoutubeCommentSniffer(object):

    CSV_HANDLER : CSVFileHandler
    COMMENT_PULLING_MODULE : CommentPullingModule
    YOUTUBE : "YouTubeResource"


    def build_youtube_client(self) -> Any:

        # Create a credentials instance from the credentials json file
        c = service_account.Credentials.from_service_account_file(
            "./creds.json",
            scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
        )

        # Build the client and return it
        return googleapiclient.discovery.build(
            serviceName="youtube",
            version="v3",
            credentials = c
        )



    def __init__(self) -> None:

        # Init rich console
        self.CONSOLE = Console()

        # Build the youtube client
        self.YOUTUBE = self.build_youtube_client()
        
        # Create a CSVFileHandler object, specifying where all of the CSV files are
        self.CSV_HANDLER = CSVFileHandler('./in')

        # Init the comment pulling module
        self.COMMENT_PULLING_MODULE = CommentPullingModule(self.YOUTUBE, self.CONSOLE)

        # Init the database module
        self.DATABASE = DatabaseHandler(out_path="./out.db")

        # Init persistent storage for query stuff
        self.PERSIST = PersistHandler(console = self.CONSOLE)

    


    def pull_comments(self) -> None:

        c, v, p = 0, 0, 0


        # Yields a channel and all of the assoc. video ids
        for channel in self.CSV_HANDLER.csv_generator():

            # If said channel is not equivalent to the last session, skip this channel
            if not self.PERSIST.satisfies_state_check(channel=channel):
                c += 1
                continue

            if c != 0:
                self.CONSOLE.log(
                    f":gear: [bold green] Skipped {c} channels"
                )
                c = 0

            # Move this here, Idk why I didn't put it here in the first place
            self.PERSIST.SAVED_STATE.push_channel(channel)

            self.CONSOLE.log(
                f':bust_in_silhouette: [bold yellow] Attempting to pull videos from channel [green underline]"{channel.channel_handle}"'
            )
            
            with self.CONSOLE.status(f'[bold yellow] Pulling Video Data for [green underline]{channel.channel_handle}[/green underline]...', spinner='monkey') as status:
            # Iterate over each video id ...
                for index, vid in enumerate(channel.video_ids):

                    # If the video is not equivalent to the last session, skip this video
                    if not self.PERSIST.satisfies_state_check(video_id=vid):
                        v += 1
                        continue

                    self.PERSIST.SAVED_STATE.push_video_id(vid)

                    # If the program gets to this point, then the state resume is completed.
                    self.PERSIST.STATE_RESUME_COMPLETE = True

                    if v != 0:
                        self.CONSOLE.log(
                            f':gear: [bold yellow] Skipped {v} videos from channel [green underline]"{channel.channel_handle}"'
                        )
                        v = 0

                    # Gather the comment threads
                    try:
                        cmt_thrds = self.COMMENT_PULLING_MODULE.getCommentThreadsFromVideoId(
                            vid, subset_replies = False
                        )
                    except HttpError as httpErr:
                        self.error_callback(httpErr, vid, channel.channel_handle)


                    if cmt_thrds is None:
                        continue # Next One!

                    while True:

                        # Gather comments from the current page of threads
                        try:
                            cmts = self.COMMENT_PULLING_MODULE.getCommentsAndRepliesFromPaginatedCommentThread( cmt_thrds )
                        except HttpError as httpErr:
                            self.error_callback(httpErr, vid, channel.channel_handle)
                            cmts = None

                        # Literally insane behaviour
                        if cmts:
                            self.DATABASE.push_comments(cmts, override_video=True, video_id=vid)

                        if not cmt_thrds.hasNextPage():
                            break

                        try:
                            cmt_thrds.next()
                        except HttpError as httpErr:
                            self.error_callback(httpErr, vid, channel.channel_handle)

                    self.CONSOLE.log(f'[green] Video Id [cyan]{vid}[/cyan] Completed ({index+1}/{channel.video_id_count})')

                # Resets the video id
                self.PERSIST.SAVED_STATE.push_video_id('')

            



    def error_callback(self, err : HttpError, video_id : str, channel_handle : str) -> None:

        reason = err.error_details[0]['reason']

        if reason == 'quotaExceeded':
            self.CONSOLE.log(
                ":x: [bold red] Query Quota Exceeded for the day. [yellow] Program Shutting down..."
            )
            self.cleanup()
            quit()

        else:
            self.CONSOLE.log(
                f":x: [bold red] Video Id = {video_id} | Channel = {channel_handle} | Reason: {reason}"
            )


    # More stuff could go here
    def cleanup(self) -> None:
        self.CONSOLE.log(
            ":sponge: [magenta bold] Cleanup method called. Pushing file state and closing database connections."
        )
        self.PERSIST.push_state_to_file()
        self.DATABASE.cleanup()



if __name__ == "__main__":

    ycs = YoutubeCommentSniffer()
    
    try:
        ycs.pull_comments()
    except KeyboardInterrupt:
        print('Keyboard Interrupt: Shutting down...')
        pass
    
    ycs.cleanup()