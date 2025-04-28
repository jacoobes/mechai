import os
import argparse
import re

audio_files = [
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/bad-ball-joint-1.mp3", "label": "bad-ball-joint-1"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/bad-ball-joint-2.mp3", "label": "bad-ball-joint-2"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/bad-battery.mp3", "label": "bad-battery"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/brake-pad.mp3", "label": "brake-pad"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/car-stopping-metal-to-metal.mp3", "label": "car-stopping-metal-to-metal"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/engine-moving-failing-tranny.mp3", "label": "engine-moving-failing-tranny"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/engine-running-without-oil.mp3", "label": "engine-running-without-oil"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/engine-seizing-up.mp3", "label": "engine-seizing-up"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/failing-water-pump.mp3", "label": "failing-water-pump"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/hole-in-muffler.mp3", "label": "hole-in-muffler"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/lifter-adjustment.mp3", "label": "lifter-adjustment"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/loose-heat-shield.mp3", "label": "loose-heat-shield"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/obstruction-of-heater-fan.mp3", "label": "obstruction-of-heater-fan"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/piston-slapping.mp3", "label": "piston-slapping"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/radiator-boiling-water.mp3", "label": "radiator-boiling-water"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/running-hole-exhaust.mp3", "label": "running-hole-exhaust"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/start-up-car-bad-exhaust.mp3", "label": "start-up-car-bad-exhaust"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/starting-break-in-exhaust.mp3", "label": "starting-break-in-exhaust"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/struts.mp3", "label": "struts"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/tranny-slipping-engine-reving.mp3", "label": "tranny-slipping-engine-revving"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/trany-slipping.mp3", "label": "trany-slipping"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/trying-to-start-car-with-dead-battery.mp3", "label": "trying-to-start-car-with-dead-battery"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/vacuum-hose-leak.mp3", "label": "vacuum-hose-leak"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/valves-tapping.mp3", "label": "valves-tapping"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/water-pump.mp3", "label": "water-pump"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/wheel-well-dust-cover-breaking-off.mp3", "label": "wheel-well-dust-cover-breaking-off"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/worn-out-break-pad.mp3", "label": "worn-out-brake-pad"},
    {"src": "https://mycarmakesnoise.com/wp-content/uploads/2021/11/worn-out-serpintine-belt.mp3", "label": "worn-out-serpentine-belt"},
]


import instaloader
from instaloader import Post
import requests
from fake_useragent import UserAgent

ua = UserAgent()
    
reeldownloads = [
    "https://www.instagram.com/reel/DFY72xSSW5I/?igsh=N2t2azdnMGJteDBi",
    "https://www.instagram.com/reel/DEkpcKrumW0/?igsh=b3diNDkzZ2l1cTJu",
    "https://www.instagram.com/reel/DFdf_xJRG83/?igsh=azVteWtjOXNhZ3B3",
    "https://www.instagram.com/reel/DHdOWdTCqVI/?igsh=dmY5MzZ2NG12Znhr",
    "https://www.instagram.com/reel/DHzNMTpM_20/?igsh=MWZxYzg0eXAyM2l4Nw==",
    "https://www.instagram.com/reel/DH_uyPaMrjH/?igsh=MTQ0OXliN2tqbzR0dg==",
    "https://www.instagram.com/reel/DIe7rUmsOKg/?igsh=enZycGl2aXQ0dWwz"
]


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

    if os.path.exists(reel_shortcode+".mp4"):
        print("insta video already exists")
        return 
    post = Post.from_shortcode(L.context, reel_shortcode)
    url = post.video_url
    if url is None: 
        print("No url found, skipping")
        return 
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(reel_shortcode+".mp4", 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)   

def youtuberloader(source: str):
    ...

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
