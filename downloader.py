import os
import argparse
import re
import subprocess
import instaloader
from instaloader import Post
import requests
from fake_useragent import UserAgent

ua = UserAgent()


def cmndownloader(url:str):
    name = url.split('/')[-1]
    response = requests.get(url, headers={ 
        'User-Agent': ua.random
    })
    if response.status_code == 200:
        with open(name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)


def instadownloader(url):
    L = instaloader.Instaloader()
    reel_shortcode = re.search(r"reel\/(.+)\/", url).group(1)

    videos = None
    with open('reels/videos.txt', 'r+') as fr:
        videos = fr.read().splitlines()
    
    with open('reels/videos.txt', 'a+') as fw:
        if reel_shortcode not in videos:
            post = Post.from_shortcode(L.context, reel_shortcode)
            url = post.video_url
            if url is None: 
                print("No url found, skipping")
                return 
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(os.path.join('reels', reel_shortcode+".mp4"), 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)  
            fw.write(reel_shortcode+"\n") 
        else: 
            print("video '{f}' already processed".format(f=id))

 

def youtuberloader(source: str):
    id = None 
    # if regular link
    if 'youtube.com' in source:
        id = re.search(r'[=|/]([0-9A-Za-z_-]{10}[048AEIMQUYcgkosw])', source).group(1)
    # if a youtube share link
    elif 'youtu.be' in source:
        id = re.search(r'/([0-9A-Za-z_-]{10}[048AEIMQUYcgkosw])\?', source).group(1)
    else:
        raise Exception('not a supported url')
    print(id)
    videos = None
    with open('yt/videos.txt', 'r+') as fr:
        videos = fr.read().splitlines()
    
    with open('yt/videos.txt', 'a+') as fw:
        if id not in videos:
           subprocess.run(['yt-dlp', source, '-P', 'yt', '-o', '%(id)s' ], check=True)
           fw.write(id+"\n") 
        else:
            print("video '{f}' already processed".format(f=id))

def get_downloaders():
    sources = {
        "cmn": cmndownloader,
        "insta": instadownloader,
        "youtube": youtuberloader
    }
    return sources

def main():
    parser = argparse.ArgumentParser(description="Downloader CLI: Find available downloaders by source.")
    downloaders = get_downloaders()
    parser.add_argument(
        "source",
        choices=list(dict.keys(downloaders)),
        help="Source to get downloaders for (cmn, insta, youtube)."
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="Optional URL to download from."
    )

    args = parser.parse_args()
    downloader = downloaders.get(args.source)
    if not downloader:
        raise Exception("downloader todesn't exist") 
    if args.url:
        print(f"\n(You provided the URL: {args.url})")
        downloader(args.url)
        # Future: You could actually perform a download here using selected tools

if __name__ == "__main__":
    main()
