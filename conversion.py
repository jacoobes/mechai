
import os
import subprocess




for x in os.listdir('./dataset'):
    # ffmpeg -i bad-piston.mp4 bad-piston.mp3 && del bad-piston.mp4       
    if x.endswith('mp4'):
        p = os.path.join('dataset', x)
        cmd = [ 
            'ffmpeg', '-i', p, p.replace('mp4', 'mp3')
        ]
        subprocess.run(cmd, check=True)
        os.remove(p)
