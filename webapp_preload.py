import os
from pathlib import Path
import chromadb
import torchaudio
from transformers.models.clap import ClapFeatureExtractor, ClapProcessor, ClapModel
import torch
import random


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
        { 'embed': embed_audio(os.path.join('dataset', p)), 'meta': { 'name': Path(p).stem } }
        for p in indb
    ]
    ids = list([str(x) for x in range(0, len(embed_data))])
    embeds = [ x['embed'] for x in embed_data]
    metadata = [x['meta'] for x in embed_data]
    
    collection.add(ids=ids, embeddings=embeds, metadatas=metadata)
    print(len(indb), len(test))
    with open('webapp_testable_sounds.txt', 'w+') as fr:
        fr.write("\n".join(test))
        
    if not os.path.exists('./uploads'):
        os.mkdir('./uploads')
        
