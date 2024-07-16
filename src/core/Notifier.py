from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap

from praw import Reddit
from praw.models.reddit.submission import Submission
from praw.models.reddit.subreddit import Subreddit
from dateutil.tz import gettz
from dataclasses import dataclass
import os, traceback, time, datetime
import requests

from . import conf

os.environ['praw_check_for_updates'] = "false"

@dataclass
class Post:
    idstr: str
    author: str
    title: str
    link: str
    flair: str
    link_flair_background_color: str
    last_post_date: datetime.datetime
    thumbnail_url: str
    subreddit_name: str
    subreddit_icon: str

class Notifier(QThread):

    postFound = Signal(Post)
    fetchFailed = Signal(str, str)

    def __init__(self, subred: str, user: str, passw: str, client_id: str, client_secret: str, retry_delay: int):
        super(Notifier, self).__init__()
        self.subred = subred
        self.reddit = Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=conf.USER_AGENT,
            username=user,
            password=passw
        )
        self.subreddit: Subreddit = self.reddit.subreddit(self.subred)
        self.count = 0
        self.current_new = ""
        self.last_found_seconds = 0
        self.retry_delay = retry_delay

    def url_to_icon(self, url):
        imgr = requests.get(url)
        if imgr.ok:
            return QPixmap(imgr.content)
        else:
            return QPixmap(conf.ICON_FILE)
        
    def run(self):
        while True:
            try:
                new_post: Submission = list(self.subreddit.new())[0]
                if self.current_new != new_post.id:
                    self.last_found_seconds = 0
                    link = 'https://www.reddit.com' + new_post.permalink
                    self.current_new = new_post.id
                    flair_text = new_post.link_flair_text
                    if flair_text and ":" in flair_text:
                        f = flair_text.split(":")
                        flair_text = f[0]
                    
                    post_time = datetime.datetime.fromtimestamp(new_post.created_utc, gettz("UTC"))
                    post = Post(
                        new_post.id, 
                        str(new_post.author), 
                        str(new_post.title), 
                        link, 
                        flair_text, 
                        new_post.link_flair_background_color, 
                        self.convert_to_local(post_time), 
                        str(new_post.thumbnail) or "",
                        self.subred,
                        self.subreddit.icon_img
                    )
                    self.postFound.emit(post)

                time.sleep(int(self.retry_delay))
                self.count += 1
            except Exception as e:
                self.fetchFailed.emit("Error", f"Erorr: Please check your configuration\n{e}\n\n{traceback.format_exc()}") 

    def convert_to_local(self, utc_dt: datetime.datetime):
        utc_dt = utc_dt.replace(tzinfo=gettz("UTC"))
        local_dt = utc_dt.astimezone(gettz("Asia/Dhaka"))
        return local_dt