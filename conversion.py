
import os
import subprocess




for x in os.listdir('./dataset'):
    # ffmpeg -i bad-piston.mp4 bad-piston.mp3 && del bad-piston.mp4       
    if x.endswith('mp3'):
        p = os.path.join('dataset', x)
        cmd = [ 
            'ffmpeg', '-i', p,
                    '-vn',
                    '-acodec', 'pcm_s16le',
                    '-ar', '48000',          # sample rate 48000
                    '-ac', '1',              # convert to mono channel instead of stereo
                    '-filter:a', 'loudnorm', # normalize audio loudness
                    p.replace('mp3', 'wav')
        ]
        subprocess.run(cmd, check=True)
        #os.remove(p)
