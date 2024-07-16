import praw
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass
import re
from . import conf


@dataclass
class Image:
    url: str
    thumbnail: str

class RedditImageDownloader:

    def __init__(self):
        config = conf.config()

        self.reddit = praw.Reddit(
            client_id=config.get(conf.CLIENT_SECTION, conf.CLIENT_ID, raw=True),
            client_secret=config.get(conf.CLIENT_SECTION, conf.CLIENT_SECRET, raw=True),
            user_agent=conf.USER_AGENT,
        )

    def convert_to(self, url: str):
        parsed_url = urlparse(url)
        image_filename = parsed_url.path.split('/')[-1]
        width_param = parse_qs(parsed_url.query).get('width', [None])[0]
        return f"https://i.redd.it/{image_filename}?width={width_param}"

    def get_url_id(self, url: str):
        matched = re.search(r'/comments/(\w+)', url)
        if matched:
            post_id = matched.group(1)
            return post_id
        else:
            return None

    def get_images(self, submission_url):
        if submission_url.startswith("http"):
            result = self.get_url_id(submission_url)
            if result:
                submission_url = result
            else:
                print("RID: Failed to download images, invalid url")
                return []
            
        submission = self.reddit.submission(submission_url)
        if "gallery" in submission.url:
            submission = self.reddit.submission(url=submission.url)
            gallery_data = submission.media_metadata 
            urls = []
        
            for image_id in gallery_data: 
                main_url = gallery_data[image_id]['s']['u'] 
                previews = gallery_data[image_id]['p']
                if len(previews) > 0:
                    thumbnail_url = previews[0]['u']
                else:
                    print(f"RID: No thumbnails found for {submission_url}")
                    thumbnail_url = main_url
                print("THUMBOR", thumbnail_url)
                img = Image(self.convert_to(main_url), thumbnail_url)
                urls.append(img)

            return urls
        
        return [Image(url=submission.url, thumbnail=submission.url)]



# r = get_images('https://www.reddit.com/r/computers/comments/18gs0c6/')
# pprint(r)

# https://i.redd.it/ncg19my0lw5c1.jpg?width=1080&crop=smart&auto=webp&s=72fb1f3fee4bd93b9b05ac2a568dc5d60db7c347