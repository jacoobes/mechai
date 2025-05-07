import torchaudio
from transformers.models.clap import ClapFeatureExtractor, ClapProcessor, ClapModel
import torch

# Load the CLAP model and processor
model_name = "laion/clap-htsat-unfused"
processor = ClapProcessor.from_pretrained(model_name)
feature_extractor = ClapFeatureExtractor.from_pretrained(model_name)
model = ClapModel.from_pretrained(model_name).to("cuda" if torch.cuda.is_available() else "cpu")

def load_audio(wav_path, target_sr=48000):
    waveform, sr = torchaudio.load(wav_path)  # returns (channels, samples) tensor
    # print("loading", wav_path, sr)
    if waveform.shape[0] != 1:
        raise Exception(wav_path + " must be mono channel")
    return waveform

def embed_audio(wav_path):
    waveform = load_audio(wav_path)
    # print(waveform.shape)
    # 2. Prepare inputs for CLAP
    #inputs = processor(audios=waveform[0], sampling_rate=48000,  return_tensors="pt", padding=True)
        

    with torch.no_grad():
        inputs = feature_extractor(waveform[0], sampling_rate=48000, return_tensors="pt")
        audio_feats = model.get_audio_features(**inputs)  # (batch_size=1, 512)

    return audio_feats.cpu().numpy().squeeze()


def select_related_audio(collection, audio):
    embed = embed_audio(audio)
    query= collection.query(query_embeddings=embed, n_results=5)
    return query
