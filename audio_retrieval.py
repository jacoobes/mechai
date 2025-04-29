import torchaudio
import laion_clap

model = CLAP(version='2023', use_cuda=True)  # set use_cuda=True if you have a GPU

def embed_audio(wav_path):
    waveform, sr = torchaudio.load(wav_path)
    
    # Convert to 48kHz mono (CLAP expects this)
    if sr != 48000:
        waveform = torchaudio.functional.resample(waveform, orig_freq=sr, new_freq=48000)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    # Get embedding
    embedding = model.get_audio_embedding_from_data(x=waveform, use_tensor=True)
    return embedding.detach().cpu().numpy()  # shape: (1, 512)



print(embed_audio('./dataset/struts.wav'))
