import os
from pathlib import Path
import torchaudio
from transformers.models.clap import ClapFeatureExtractor, ClapProcessor, ClapModel
import torch

# Load the CLAP model and processor
model_name = "laion/clap-htsat-unfused"
processor = ClapProcessor.from_pretrained(model_name)
feature_extractor = ClapFeatureExtractor.from_pretrained(model_name)
model = ClapModel.from_pretrained(model_name).to("cuda" if torch.cuda.is_available() else "cpu")


def embed_audio(wav_path):
    waveform = load_audio(wav_path)
    # print(waveform.shape)
    # 2. Prepare inputs for CLAP
    filename = Path(wav_path).stem
    #inputs = processor(audios=waveform[0], sampling_rate=48000,  return_tensors="pt", padding=True)
        

    with torch.no_grad():
        inputs = feature_extractor(waveform[0], sampling_rate=48000, return_tensors="pt")
        audio_feats = model.get_audio_features(**inputs)  # (batch_size=1, 512)

    return audio_feats.cpu().numpy().squeeze()

    # 4. Convert to NumPy
    return audio_feats.cpu().numpy().squeeze()


    

import usearch
import usearch.index

index = usearch.index.Index(ndim=512)
i = 0
for p in os.listdir('./dataset'):
    if  p.endswith('wav'):
        p = os.path.join('dataset', p)
        index.add(i, embed_audio(p))
        print(i, p)
        i+=1

searchembed = embed_audio('./dataset/bad-piston.wav')
matches = index.search(searchembed, 10)  # Find 10 nearest neighbors


print(matches.to_list())
