from flask import Flask, request, abort, Response
from flask_cors import CORS
import audio

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

INDEXED_SONGS_DIR = "D:/Datasets/Music/indexed/"


@app.route('/query-song', methods=['POST'])
def query_song_():
    
    try:
        audiofile = request.files["audio"]
    except KeyError:
        abort(400)
    
    return audio.query_song(audiofile)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)