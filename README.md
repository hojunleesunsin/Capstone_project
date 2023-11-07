![Status Classify Smart Baby Sleeper](https://capsule-render.vercel.app/api?type=waving&color=auto&height=300&section=header&text=Status%20Classify%20Smart%20Baby%20Sleeper&fontSize=50)

<a href = "https://github.com/kdk0411/Audio_Classification_Model"></a>

## 목차
- [목차](#목차)
- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [프로젝트 목표](#프로젝트-목표)
- [기술 스택](#기술-스택)
  - [FLASK](#flask)
  - [Node.js](#nodejs)

<a href = "https://github.com/kdk0411/Audio_Classification_Model">모델 학습 및</a>

## 프로젝트 개요
아기 상태 감별 스마트 베이비 슬리퍼는 부모가 아기를 돌보는 데 도움을 주는 스마트 기기입니다.  
이 프로젝트의 목표는 아기의 울음소리를 감지하고 분석하여 부모에게 알림을 보내고, 아기가 왜 울고 있는지를 이해하고 조치를 취할 수 있도록 돕는 것입니다. 또한, 아기의 울음을 감지하면 자동으로 백색소음을 발생시키고 침대를 흔들어 아기를 달래며, 부모가 언제든 실시간 스트리밍을 통해 아기를 모니터링할 수 있습니다.

## 주요 기능
- 아기 울음소리 감지 및 분류
- 부모에게 알림 전송
- 백색소음 발생
- 침대 흔들림 기능
- 실시간 카메라 스트리밍

## 프로젝트 목표
이 프로젝트의 목표는 부모들이 아기를 더 효과적으로 돌볼 수 있도록 돕는 스마트 베이비 슬리퍼를 개발하는 것입니다. 부모의 육아 스트레스를 줄이고, 아기의 안전과 편안함을 증진시키는 것을 목표로 합니다.

## 기술 스택
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" width="50%" height="150"><img src="https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white" width="50%" height="150">

위의 프로젝트에서는 마이크 센서값을 전달받아 학습된 인공지능 모델에 적용시켜서 아기의 상태를 분류하기 위한 Flask 서버와 온습도 값을 전달받아 아기의 대소변 유무를 파악하기 위한 Node.js 서버 두가지로 구성하였다.  

서버를 두가지로 구성하게된 이유는 더 많은 기술 경험을 쌓아보기 위함과 각 서버에 작업을 분산시켜 성능을 향상시키기 위해서이다.
<br>
<br>
<br>

***
### FLASK
실시간 오디오 데이터 처리 및 예측을 목표로 하며, Flask 웹 애플리케이션과 Socket.IO를 기반으로 구현하였습니다.  

Flask 서버는 venv 가상환경을 활성화하여 가상환경에서 실행하였습니다.

**핵심내용**
- Flask 웹 어플리케이션을 사용하여 웹 서버를 구동하며, 클라이언트와의 통신을 처리합니다.
- Flask-SocketIO확장을 사용하여 웹 소켓 통신을 활성화하고 실시간 통신을 지원합니다.
- 라즈베리파이 클라이언트로부터 전달받은 오디오 데이터를 디코딩하고, 서버에 저장합니다.
- 저장된 오디오 데이터를 분석하고 예측하기 위해 Keras를 사용한 딥러닝 모델을 로드하고, AudioPredictor 클래스를 사용하여 예측 작업을 수행합니다.
- 예측 결과를 클라이언트로 다시 전송하고, 사용이 완료된 오디오 파일을 삭제합니다.
<br>
<br/>

```python
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    
@app.route('/')
def home():
    return 'Welcome to my Flask Server!'   

@socketio.on('audio_data')
def handle_audio_data(data):
    base64audio = data.get('audio_data')
```

아기의 울음소리를 실시간으로 전달받고 처리하기위해 SocketIO를 사용하였습니다.  

라즈베리파이 클라이언트로 부터 'audio_data'요청을 받게 되면 전달받은 오디오 데이터를 base64audio 변수에 저장하게 됩니다.  
<br>


```python
    audio_data = base64.b64decode(base64audio)  
    
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_audio_file.wav"  
    
    # 오디오 파일 저장
    with open(os.path.join(audio_dir, filename), 'wb') as f:
        f.write(audio_data)

    print(f"Received audio data of length {len(audio_data)}")
    emit('response', {'message': 'Audio data received and saved'})
```

오디오 데이터를 base64 모듈을 사용하여 디코딩한 후 지정된 파일 경로에 저장합니다.  
<br>

```python
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
        
    socketio.emit('prediction', 
    {'prediction': int(predicted_classes[0])})
```

audiopredictor.py 파일의 AudioPredictor 클래스를 import하여 음성을 기준에 따라 분류하고 중복 데이터 제거를 위해 오디오 데이터를 삭제하고 분류 결과를 안드로이드 앱으로 전송 해줍니다.  
<br>

***
### Node.js
Node.js 서버 역시 실시간으로 온습도 데이터 처리를 목표로 하며, Node.js 웹 애플리케이션과 Socket.IO를 기반으로 구현하였고 Express 웹 프레임워크를 사용하였습니다.  

**핵심내용**
- Node.js 웹 어플리케이션을 사용하여 웹 서버를 구동하며, 클라이언트와의 통신을 처리합니다.
- socket.io확장을 사용하여 웹 소켓 통신을 활성화하고 실시간 통신을 지원합니다.
- 라즈베리파이 클라이언트로부터 전달받은 온습도 데이터를 기준 수치 이상인지 확인하여 대소변 유무를 안드로이드 앱으로 전달합니다.
  
```javascript
server.listen(port, '192.168.35.49', () => {
  console.log(`Server listening on port ${port}`); // 서버 실행 시 로그 출력
  
  io.on('connection', (socket) => {
    console.log('Client connected'); // 클라이언트 연결 시 로그 출력
    socket.on('dhtData', (data) => {   // 클라이언트로부터 dhtData 메시지를 받으면
      console.log('Received dhtData: ', data);

      let emitValue;
      // 온도와 습도 값이 모두 기준수치 이상인지 확인
      if (data.temperature >= 29 && data.humidity >= 99) {
        emitValue = { "dhtData": 1 };
      } else {
        emitValue = { "dhtData": 0 };
      }
      io.emit('dhtData', emitValue);

      emitValue = null;
    });
  });
});
```

라즈베리파이 클라이언트로부터 dhtData 요청을 받으면 온습도 값을 넘겨 받아 온도가 29, 습도가 99이상이면 대소변을 눈 것으로 판단하여 안드로이드 앱으로 판단 정보를 전달합니다.