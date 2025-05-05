import os
from pathlib import Path
import chromadb
import torchaudio
from transformers.models.clap import ClapFeatureExtractor, ClapProcessor, ClapModel
import torch
import random
import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect("audio_storage.db")
cursor = conn.cursor()

# Create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS audio_files (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    audio_data BLOB NOT NULL
)
""")

conn.commit()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') 

def load_audio(wav_path, target_sr=48000):
    waveform, sr = torchaudio.load(wav_path)  # returns (channels, samples) tensor
    print("loading for embedding:", wav_path, 'sample rate=', sr)
    if waveform.shape[0] != 1:
        raise Exception(wav_path + " must be mono channel")
    return waveform.to(device)

def embed_audio(wav_path):
    waveform = load_audio(wav_path)

    with torch.no_grad():
        inputs = feature_extractor(waveform[0], sampling_rate=48000, return_tensors="pt")
        audio_feats = model.get_audio_features(**inputs)  # (batch_size=1, 512)

    return audio_feats.cpu().numpy().squeeze()

def read_blob(x):
    with open(os.path.join('dataset', x), 'rb') as fr: 
        audio_blob = fr.read()
    return audio_blob;

if __name__ == '__main__':
    # Load the CLAP model and processor
    model_name = "laion/clap-htsat-unfused"
    processor = ClapProcessor.from_pretrained(model_name)
    feature_extractor = ClapFeatureExtractor.from_pretrained(model_name)
    model = ClapModel.from_pretrained(model_name).to(device)


    # Establish client
    chroma_client = chromadb.PersistentClient(path="webapp_db/")
    collection = chroma_client.create_collection(
        name="documents",
    )

    embeddable_files = [x for x in os.listdir('./dataset') if x.endswith('wav')]
    embeddable_files = random.sample(embeddable_files, len(embeddable_files))
    split_index = int(len(embeddable_files) * 0.85)
    indb = embeddable_files[:split_index]
    test = embeddable_files[split_index:]
    
    embed_data = [
        { 'id': f'doc_{i}', 'embed': embed_audio(os.path.join('dataset', p)), 'meta': { 'name': Path(p).stem }, 'raw': read_blob(p) }
        for i,p in enumerate(indb)
    ]
    ids = [x['id'] for x in embed_data]
    embeds = [ x['embed'] for x in embed_data]
    metadata = [x['meta'] for x in embed_data]
    
    collection.add(ids=ids, embeddings=embeds, metadatas=metadata)
    print(len(indb), len(test))
    with open('webapp_testable_sounds.txt', 'w+') as fr:
        fr.write("\n".join(test))

    for x in embed_data:
        cursor.execute("INSERT INTO audio_files (id, filename, audio_data) VALUES (?, ?, ?)", 
            (x['id'], x['meta']['name'], x['raw']))
        ...

    if not os.path.exists('./uploads'):
        os.mkdir('./uploads')
    if not os.path.exists('./static'):
        os.mkdir('./static')
            
   
    conn.close()
