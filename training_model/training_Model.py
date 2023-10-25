import pandas as pd
import numpy as np
import librosa
import os
import pathlib
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, concatenate, Conv2D, Reshape, BatchNormalization, Activation, Add, Flatten, Dense
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import LabelEncoder, StandardScaler
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.losses import BinaryCrossentropy
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import LeakyReLU
# from tensorflow.keras.losses import BinaryCrossentropy

# hop_length

import time
start = time.time()

class AudioClassifier:
    def __init__(self, wav_path, csv_path):
        self.wav_path = wav_path
        self.csv_path = csv_path

    def process_data(self):
        X_mfcc = []
        X_mel_spec = []
        labels = []
        data_dir = pathlib.Path(self.wav_path)
        all_wav_paths = sorted(list(data_dir.glob('*.wav')))

        df = pd.read_csv(self.csv_path)
        cry_audio_file = df["Cry_Audio_File"]
        label = df["Label"]

        max_length = 188

        for wav_path_dir in all_wav_paths:
            file_name = os.path.basename(wav_path_dir)
            index = cry_audio_file[cry_audio_file == file_name].index[0]
            label_value = label[index]

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
            labels.append(label_value)

        X_mfcc = np.array(X_mfcc)
        X_mel_spec = np.array(X_mel_spec)
        labels = np.array(labels)
        return X_mfcc, X_mel_spec, labels

    def preprocess_data(self):
        X_mfcc, X_mel_spec, labels = self.process_data()

        scaler_mfcc = StandardScaler()
        scaler_mel_spec = StandardScaler()

        X_mfcc_scaled = scaler_mfcc.fit_transform(X_mfcc.reshape(-1, X_mfcc.shape[-1])).reshape(X_mfcc.shape)
        X_mel_spec_scaled = scaler_mel_spec.fit_transform(X_mel_spec.reshape(-1, X_mel_spec.shape[-1])).reshape(X_mel_spec.shape)

        label_encoder = LabelEncoder()
        labels_encoded = label_encoder.fit_transform(labels)
        num_classes = len(label_encoder.classes_)

        return X_mfcc_scaled, X_mel_spec_scaled, labels_encoded, label_encoder, num_classes

train_csv_path = "/content/drive/MyDrive/Baby_Sound/Hungry/Classificant_Audio_data/New_train_Audio.csv"
train_data_dir = "/content/drive/MyDrive/Baby_Sound/Hungry/Classificant_Audio_data"

test_csv_path = "/content/drive/MyDrive/Baby_Sound/Hungry/Classificant_Audio_data_test/test_Audio_New.csv"
test_data_dir = "/content/drive/MyDrive/Baby_Sound/Hungry/Classificant_Audio_data_test"

train_classifier = AudioClassifier(train_data_dir, train_csv_path)
X_train_mfcc, X_train_mel_spec, y_train, label_encoder, num_classes = train_classifier.preprocess_data()

test_classifier = AudioClassifier(test_data_dir, test_csv_path)
X_test_mfcc, X_test_mel_spec, y_test, _, _ = test_classifier.preprocess_data()

# 데이터 분할 random_state=42
X_train_mfcc_scaled, X_val_mfcc_scaled, X_train_mel_spec_scaled, X_val_mel_spec_scaled, y_train_encoded, y_val_encoded = train_test_split(
    X_train_mfcc, X_train_mel_spec, y_train, test_size=0.2, stratify=y_train)

print(f'X_train_mfcc_scaled : {X_train_mfcc_scaled.shape}')
print(f'X_val_mfcc_scaled : {X_val_mfcc_scaled.shape}')
print(f'X_train_mel_spec_scaled : {X_train_mel_spec_scaled.shape}')
print(f'X_val_mel_spec_scaled : {X_val_mel_spec_scaled.shape}')
print(f'y_train_encoded : {y_train_encoded.shape}')
print(f'y_val_encoded : {y_val_encoded.shape}')
print(f'num_classes : {num_classes}')

def residual_block(inputs, filters, kernel_size):
    x = Conv2D(filters, kernel_size, padding='same')(inputs)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Conv2D(filters, kernel_size, padding='same')(x)
    x = BatchNormalization()(x)
    x = Add()([inputs, x])
    x = Activation('relu')(x)
    return x

# 모델 생성
mfcc_input = Input(shape=X_train_mfcc_scaled.shape[1:])
mfcc_reshaped = Reshape((*X_train_mfcc_scaled.shape[1:], 1))(mfcc_input)
mfcc_model = Conv2D(32, kernel_size=(4, 4))(mfcc_reshaped)
mfcc_model = BatchNormalization()(mfcc_model)
mfcc_model = LeakyReLU()(mfcc_model)

# Residual Block 추가
mfcc_model = residual_block(mfcc_model, 32, (4, 4))
mfcc_model = residual_block(mfcc_model, 32, (4, 4))

mel_spec_input = Input(shape=(X_train_mel_spec_scaled.shape[1], X_train_mel_spec_scaled.shape[2], 1))
mel_spec_model = Conv2D(32, kernel_size=(4, 4))(mel_spec_input)
mel_spec_model = BatchNormalization()(mel_spec_model)
mel_spec_model = LeakyReLU()(mel_spec_model)

# Residual Block 추가
mel_spec_model = residual_block(mel_spec_model, 32, (4, 4))
mel_spec_model = residual_block(mel_spec_model, 32, (4, 4))

mfcc_model_flatten = Flatten()(mfcc_model)
mel_spec_model_flatten = Flatten()(mel_spec_model)
combined = concatenate([mfcc_model_flatten, mel_spec_model_flatten])

common = Dense(64, activation='relu')(combined)
# output = Dense(1, activation='sigmoid')(common)
output = Dense(num_classes, activation='softmax')(common)

learning_rate = 0.00006  # 학습률 값
optimizer = Adam(learning_rate=learning_rate)
model = Model(inputs=[mfcc_input, mel_spec_input], outputs=output)
model.compile(loss='sparse_categorical_crossentropy', optimizer='Adam', metrics=['accuracy'])
model.fit([X_train_mfcc_scaled, X_train_mel_spec_scaled], y_train_encoded, batch_size=16, shuffle=True, epochs=10, validation_data=([X_val_mfcc_scaled, X_val_mel_spec_scaled], y_val_encoded))

# 모델 평가
loss, accuracy = model.evaluate([X_test_mfcc, X_test_mel_spec], y_test)
model.save('Audio_Classify_Model.h5')
print("Test Loss:", loss)
print("Test Accuracy:", accuracy * 100, "%")

run_time = round(time.time() - start, 2)
print("Run_time :", run_time, "sec")