// 모듈 임포트
const express = require('express'); // Express 웹 애플리케이션 프레임워크 임포트
const app = express(); // Express 앱 인스턴스 생성
const server = require('http').createServer(app); // HTTP 서버 생성
const io = require('socket.io')(server); // Socket.IO를 사용한 통신을 위해 서버 인스턴스에 연결

//서버 포트 설정
const port = 8080;

// 서버 및 실행
server.listen(port, '192.168.35.49', () => {
  console.log(`Server listening on port ${port}`); // 서버 실행 시 로그 출력
  
  io.on('connection', (socket) => {
    console.log('Client connected'); // 클라이언트 연결 시 로그 출력
    socket.on('dhtData', (data) => {   // 클라이언트로부터 dhtData 메시지를 받으면
      console.log('Received dhtData: ', data);

      let emitValue;
      // 온도와 습도 값이 모두 10 이상인지 확인
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
 