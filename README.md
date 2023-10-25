![Status Classify Smart Baby Sleeper](https://capsule-render.vercel.app/api?type=waving&color=auto&height=300&section=header&text=Status%20Classify%20Smart%20Baby%20Sleeper&fontSize=50)

## 목차
- [목차](#목차)
- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [프로젝트 목표](#프로젝트-목표)
- [기술 스택](#기술-스택)

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
언급할만한 프로그래밍 언어, 프레임워크, 라이브러리 등 넣기
