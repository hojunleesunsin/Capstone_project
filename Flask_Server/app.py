from keras.models import load_model
from flask import Flask #, request, Response
from flask_socketio import SocketIO, emit
#import numpy as np
import os
from datetime import datetime
import base64
from audiopredictor import AudioPredictor
# import soundfile as sf

app = Flask(__name__)
socketio = SocketIO(app)

model_path = "/home/parkdongsoo/project2/venv/Audio_Classify_Model_0.2_97.h5"
audio_dir = "/home/parkdongsoo/project2/venv/audio"

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    
@app.route('/')
def home():
    return 'Welcome to my Flask Server!'   

@socketio.on('audio_data')
def handle_audio_data(data):
    base64audio = data.get('audio_data')
    
    audio_data = base64.b64decode(base64audio)  # assuming data is sent as {'audio': base64_encoded_data}
# audio_data = data['audio']  # assuming data is sent as {'audio': binary_data}
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_audio_file.wav"  # create a filename for the audio file
    
    # Save the audio file
    with open(os.path.join(audio_dir, filename), 'wb') as f:
        f.write(audio_data)

    print(f"Received audio data of length {len(audio_data)}")
    emit('response', {'message': 'Audio data received and saved'})
    
    predictor = AudioPredictor(model_path, audio_dir)
    predicted_classes, _ = predictor.predict_classes()
    print(predicted_classes)
    print(predicted_classes[0])
    
        # Delete the file after prediction
    if os.path.exists(os.path.join(audio_dir, filename)):
        os.remove(os.path.join(audio_dir, filename))
        print(f"Deleted the file: {filename}")
    else:
        print("The file does not exist")
        
    socketio.emit('prediction', {'prediction': int(predicted_classes[0])})
    # Send the prediction back to the client
    
    
if __name__ == "__main__":
    socketio.run(app, host="192.168.35.49", port=3000, debug=True)