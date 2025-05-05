from uuid import uuid4
from flask import Flask, render_template, render_template_string, request, Response, jsonify
from markupsafe import escape
import openai
from dotenv import load_dotenv
import chromadb
from audio_embed import embed_audio
import sqlite3

SERVER_NAME=""
APPLICATION_ROOT=""

app = Flask(
    __name__
)
app.config['SERVER_NAME']='localhost:5000'
app.config['PREFERRED_URL_SCHEME'] = 'http'
app.config['APPLICATION_ROOT'] = '/'

# Connect to (or create) the database
conn = sqlite3.connect("audio_storage.db")
cursor = conn.cursor()





# Load environment variables
load_dotenv()

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

with open('./key.txt', 'r') as fr:
    api_key = fr.read().strip()

openai_client = openai.OpenAI(api_key=api_key)
chroma_client = chromadb.PersistentClient(path="webapp_db/")
collection = chroma_client.get_collection('documents')

user = { 
    'query': None,
    'audio': None
}

prompt = """
You are an AI Mechanic who is diagnosing car issues by sound and description.

Guidelines:
1. You must try to use the provided names of audio clips and the description to figure out the issue. ALWAYS reference the sound and its name
   that were used to solve the issue.
2. You must not produce any information that is not in the provided context.
3. If the provided context does not contain the answer, you should respond with the list of similar noises provided in the context

Markdown should be rendered by wrapping it in <md-block> </md-block> tags, instead of a codeblock.
Good example: 
<md-block>
	# Heading
	* List item 1
	* List item 2
</md-block>

Bad example:
```md
# Heading
* List item 1
* List item 2
```

A machine provided similar sounds, listed by name. It is possible the machine may not capture any sounds.
Be aware that some (or even all) audio clips may not be relevant to the issue:
{context}


Here is the description: {description}
Your response:"""

def select_related_audio(audio):
    embed = embed_audio(audio)
    query= collection.query(query_embeddings=embed, n_results=5)
    return query


def openai_chat_creation(description, topn_audio):
    yield from openai_client.chat.completions.create( 
        model="o3-mini",
        messages= [
           { 'role': 'system', 'content': prompt.format(description=description, context={str(topn_audio['metadatas'])})}
        ],
        stream=True
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream', methods=['GET'])
def stream():
    # Stream AI responses as Server-Sent Events

    def generate():
        with app.app_context():
            # Call OpenAI ChatCompletion with streaming
            yield f"""data: <p sse-swap="message">thinking.....</p>\n\n"""
            final_content = ""
            try:
                topn_audio = select_related_audio(user['audio'])
                print(topn_audio)
                for chunk in openai_chat_creation(user['query'], topn_audio):
                    content = chunk.choices[0].delta.content
                    if content:
                        content=content.replace("\n", "\ndata:", 1)
                        final_content += content
                        yield f"""data: <p sse-swap="message">{final_content}</p><p hx-swap="preterminate"></p>\n\n"""
                yield f"""event: terminate\ndata: <p hx-target="stream-body">{final_content}</p>{render_template('audio_list.html', links=topn_audio['ids'][0])}\n\n"""
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                yield f"""event: terminate\ndata: <p hx-target="stream-body">{final_content}</p>\n\n"""

    return Response(generate(), mimetype='text/event-stream')


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get('usermessage')
    caraudio = (request.files.get('caraudio'))
    audiopath = f'./uploads/{uuid4()}.wav'
    if caraudio:
        if not allowed_file(caraudio.filename):
             return Response("""
                <div> 
                   <p>Audio has to be mp3 or wav</p>
                </div>
            """, status=403)

        caraudio.save(audiopath)


    if not user_message or user_message.isspace():
        return Response("""
            <div> 
               <p>Message can't be empty!</p>
            </div>
        """, status=403)

    user['query'] = user_message
    user['audio'] = audiopath 

    return f"""
    <div>
        <h3>You</h3>
        <p class="user">{user_message}</p>
        <h3>Mechai</h3>
        <div sse-connect="/stream" 
           id="stream-body"
           sse-close="terminate"> 
           <p sse-swap="message"> </p>
        </div>
    </div>
    """

def get_audio_file(file_id: str):
    cursor.execute("SELECT filename, audio_data FROM audio_files WHERE id = ?", (file_id,))
    result = cursor.fetchone()
    conn.close()
    return result

@app.route('/audio', methods=['GET'])
def audio_url():
    id = request.args.get('audio_id')
    audio = get_audio_file(file_id=id)    
    return Response(audio)
    ...


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
        print("closing\n");
        conn.close()
