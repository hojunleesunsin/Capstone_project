import numpy as np
import librosa
import pathlib
from sklearn.preprocessing import StandardScaler, LabelEncoder
from keras.models import load_model


# from tensorflow import 

class AudioPredictor:
    def __init__(self, model_path, audio_dir):
        self.model_path = model_path
        self.audio_dir = audio_dir

    def preprocess_data(self):
        X_mfcc = []
        X_mel_spec = []
        data_dir = pathlib.Path(self.audio_dir)
        all_wav_paths = sorted(list(data_dir.glob('*.wav')))

        max_length = 188

        for wav_path_dir in all_wav_paths:
            y, sr = librosa.load(wav_path_dir, sr=16000, duration=6)

            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            if mfcc.shape[1] > max_length:
                mfcc = mfcc[:, :max_length]

            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
            mel_spec = librosa.amplitude_to_db(mel_spec, ref=np.max)
            if mel_spec.shape[1] > max_length:
                mel_spec = mel_spec[:, :max_length]

            X_mfcc.append(mfcc)
            X_mel_spec.append(mel_spec)

        X_mfcc = np.array(X_mfcc)
        X_mel_spec = np.array(X_mel_spec)

        return X_mfcc, X_mel_spec

    def predict_classes(self):
        X_mfcc, X_mel_spec = self.preprocess_data()

        scaler_mfcc = StandardScaler()
        scaler_mel_spec = StandardScaler()

        X_mfcc_scaled = scaler_mfcc.fit_transform(X_mfcc.reshape(-1, X_mfcc.shape[-1])).reshape(X_mfcc.shape)
        X_mel_spec_scaled = scaler_mel_spec.fit_transform(X_mel_spec.reshape(-1, X_mel_spec.shape[-1])).reshape(X_mel_spec.shape)

        model = load_model(self.model_path)

        predictions = model.predict([X_mfcc_scaled, X_mel_spec_scaled])
        predicted_classes = np.argmax(predictions, axis=1)

        return predicted_classes, predictions

# model_path = "C:/Users/hongp/Project/venv/Audio_Classify_Model_0.2_97.h5"
# audio_dir = "C:/Users/hongp/Project/venv/audio"  # 새로운 음성 데이터가 저장된 경로로 변경해주세요

# predictor = AudioPredictor(model_path, audio_dir)
# predicted_classes, predictions = predictor.predict_classes()

# print('Predicted Classes:', predicted_classes)
# print('Predictions:', predictions)