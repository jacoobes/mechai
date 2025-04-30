import os
from pathlib import Path
import sqlite3
import chromadb
from flask import json
import torchaudio
from transformers.models.clap import ClapFeatureExtractor, ClapProcessor, ClapModel
import torch

def load_audio(wav_path, target_sr=48000):
    waveform, sr = torchaudio.load(wav_path)  # returns (channels, samples) tensor
    print("loading", wav_path, sr)
    if waveform.shape[0] != 1:
        raise Exception(wav_path + " must be mono channel")
    return waveform

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

tables = f"""
CREATE TABLE audio_vectors IF NOT EXISTS (
    id SERIAL PRIMARY KEY AUTOINCREMENT,
    vector JSON NOT NULL,
    name TEXT NOT NULL
);
"""

insert_script = """
    INSERT INTO audio_vectors (vector, name)
    VALUES (?, ?)
"""




if __name__ == '__main__':
    # Load the CLAP model and processor
    model_name = "laion/clap-htsat-unfused"
    processor = ClapProcessor.from_pretrained(model_name)
    feature_extractor = ClapFeatureExtractor.from_pretrained(model_name)
    model = ClapModel.from_pretrained(model_name).to("cuda" if torch.cuda.is_available() else "cpu")


    # Establish client
    chroma_client = chromadb.PersistentClient(path="webapp_db/")
    collection = chroma_client.create_collection(
        name="documents",
    )
    should_embed=True
    embed_data = [
        { 'embed': embed_audio(os.path.join('dataset', p)), 'meta': { 'name': Path(p).stem } }
        for p in os.listdir('./dataset') if p.endswith('wav')
    ]
    ids = list([str(x) for x in range(0, len(embed_data))])
    embeds = [ x['embed'] for x in embed_data]
    metadata = [x['meta'] for x in embed_data]
    
    collection.add(ids=ids, embeddings=embeds, metadatas=metadata)
    

        
