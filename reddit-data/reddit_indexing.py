import bz2, re
import lzma
from datetime import datetime
import io
import zstandard as zstd

ID_REGEX = re.compile(' id="([^"]*)"')
URL_REGEX = re.compile(' url="([^"]*)"')
TITLE_REGEX = re.compile(' title="([^"]*)"')
'''
{"parent_id":"t1_c12a5x","id":"c12a9f","edited":false,"author_flair_text":null,"author":"cal_01","retrieved_on":1473816028,"distinguished":null,"gilded":0,"stickied":false,"link_id":"t3_129rr","subreddit_id":"t5_6","controversiality":0,"body":"Prose and style are just as important as factual information.\r\n\r\nEveryone knows that Cheney is horrible; there is no need to supply more evidence. Hence, the article is brilliant because he articulates the public opinion so well.","created_utc":1170311382,"author_flair_css_class":null,"score":9,"ups":9,"subreddit":"reddit.com"}
'''

def get_body(el):
        filtered_body = "none"
        r1 = re.findall(r"subreddit\":\"(.*?)\".",el)
        body = re.findall(r"body\":\"(.*?)\".",el)#"body":"bla bla
        ids = re.findall(r"\"id\":\"(.*?)\".",el)#"body":"blabla
        utc = re.findall(r"\"created_utc\":\"(.*?)\".",el)#
        
        dt_object = None
        if len(utc) > 0:
            dt_object = datetime.fromtimestamp(int(utc[0]))           
        else:
            utc = re.findall(r"\"created_utc\":(.*?)[,}]",el)
            dt_object = datetime.fromtimestamp(int(utc[0]))
            
        y,m,d =  str(dt_object).split()[0].split("-")
        body = body[0].strip()
        return ids[0],r1[0], body,y,m,d 
    
class RedditData:
    def __init__(self, id, subreddit, body,y=None,m=None,d=None):
        self.id = id
        self.subreddit = subreddit
        self.body = body
        self.y = y
        self.m = m
        self.d = d
       

    @classmethod
    def iterator_from_file(cls, filename):
        
        if filename.endswith(".bz2"):
            f = bz2.open(filename, "rt", encoding='utf-8')
        elif filename.endswith("xz"):
            f = lzma.open(filename, "r")
        elif filename.endswith("zst"):
            f = open(filename, 'rb')
        else:
            f = open(filename, encoding='utf-8')
        text_buffer = []
        id = url = title = None
        
        dctx = zstd.ZstdDecompressor()
        if filename.endswith("zst"):
            with dctx.stream_reader(f) as reader:
                wrap = io.TextIOWrapper(io.BufferedReader(reader), encoding='utf8')
                for post in wrap:
                    redditdata = get_body(post) 
                    if redditdata:
                        id, subreddit, body,y,m,d = redditdata
                        yield cls(id, subreddit, body,y,m,d) 
        else:            
            for post in f:
                if filename.endswith("xz"):
                    post = post.decode('utf-8')
                redditdata = get_body(post) 
                if redditdata:
                    id, subreddit, body,y,m,d = redditdata
                    yield cls(id, subreddit, body,y,m,d) 
