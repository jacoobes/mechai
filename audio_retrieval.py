import os
import torchaudio
from transformers.models.clap import ClapProcessor, ClapModel
import torch

# Load the CLAP model and processor
model_name = "laion/clap-htsat-unfused"
processor = ClapProcessor.from_pretrained(model_name)
model = ClapModel.from_pretrained(model_name).to("cuda" if torch.cuda.is_available() else "cpu")

def load_audio(wav_path, target_sr=48000):
    waveform, sr = torchaudio.load(wav_path)  # returns (channels, samples) tensor
    print("loading", wav_path, sr)
    if waveform.shape[0] != 1:
        raise Exception(wav_path + " must be mono")
    return waveform

def embed_audio(wav_path):
    waveform = load_audio(wav_path)
    # print(waveform.shape)
    # 2. Prepare inputs for CLAP
    inputs = processor(audios=waveform[0], sampling_rate=48000,  return_tensors="pt")

    with torch.no_grad():
        audio_feats = model.get_audio_features(**inputs)  # (batch_size=1, 512)

    return audio_feats.cpu().numpy().squeeze()

    # 4. Convert to NumPy
    return audio_feats.cpu().numpy().squeeze()


    

import usearch
import usearch.index

index = usearch.index.Index(ndim=512)
i = 0
for p in os.listdir('./dataset'):
    if p != 'bad-piston.wav' and p.endswith('wav'):
        p = os.path.join('dataset', p)
        index.add(i, embed_audio(p))
        print(i, p)
        i+=1

searchembed = embed_audio('./dataset/bad-piston.wav')
matches = index.search(searchembed, 10)  # Find 10 nearest neighbors


print(matches.to_list())
