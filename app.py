from flask import Flask, request, abort, Response
from flask_cors import CORS
import audio

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

INDEXED_SONGS_DIR = "D:/Datasets/Music/indexed/"

counter_ = 0

@app.after_request
def after_request(response: Response):
    print(response.json)
    return response

@app.route('/query-song', methods=['POST'])
def query_song_():
    
    try:
        audiofile = request.files["audio"]
    except KeyError:
        abort(400)

    # audiofile.save("D:/Datasets/Music/TESTING/test.wav")
    # audiofile.seek(0)
    
    return audio.query_song(audiofile)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)