
def embed_audio(path):
    audio, sr = sf.read(path) 
    embeds, _timestamps = openl3.get_audio_embedding(
        audio,
        sr,
        input_repr="mel256",
        content_type='env',
        embedding_size=512)

    # average embeddings over sliding windows.
    return embeds.mean(axis=0)



print(embed_audio('./dataset/struts.wav'))
