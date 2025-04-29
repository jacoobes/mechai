from io import BytesIO
import os
import time
from flask import Flask, render_template, request, Response, jsonify
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}
app = Flask(__name__)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream', methods=['GET'])
def stream():
    # Stream AI responses as Server-Sent Events
    def generate():
        # Call OpenAI ChatCompletion with streaming
        def generate_dummy_events(interval=1, duration=5):
            for i in range(duration):
                event_data = {
                    "choices": [{ 'delta': { 'content': 'haliburton ' }} ] 
                }
                yield event_data 
                time.sleep(0.03)

        final_content = ""
        for chunk in generate_dummy_events():
            content = chunk['choices'][0]['delta'].get('content', '')
            if content:
                final_content += content
                yield f"""data: <p sse-swap="message">{final_content}</p>\n\n"""
        yield f"""event: terminate\ndata: <p hx-target="stream-body">{final_content}</p>\n\n"""
    return Response(generate(), mimetype='text/event-stream')


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get('usermessage')
    caraudio = (request.files.get('caraudio'))
    if caraudio:
        if not allowed_file(caraudio.filename):
             return Response("""
                <div> 
                   <p>Audio has to be mp3 or wav</p>
                </div>
            """, status=403)

        iobytes = BytesIO()
        caraudio.save(iobytes)


    if not user_message or user_message.isspace():
        return Response("""
            <div> 
               <p>Message can't be empty!</p>
            </div>
        """, status=403)

    return f"""
    <div>
        <p class="user">{user_message}</p>
        <p sse-connect="/stream" 
           id="stream-body"
           sse-close="terminate"
           sse-swap="message"> </p>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True)
