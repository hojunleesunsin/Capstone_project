const fs = require('fs');
const { spawn } = require('child_process');
const io = require('socket.io-client');
const dht = require('node-dht-sensor');
const wav = require('wav');

const DHT_TYPE = 11;
const GPIO_PIN = 4;
const THRESHOLD_DB = 70; // Set the threshold value in decibels (dB)
const RECORDING_DURATION = 6; // Set the duration of recording in seconds

const outputPath = './recorded.wav'; // Path to save the WAV file
const whiteNoiseFile = './whitenoise.wav'; // Path to the white noise WAV file

const socketIO8080 = io('http://192.168.35.49:8080');  // For Temperature and Humidity Data
const socketIO3000 = io('http://192.168.35.49:3000');  // For Audio Data

socketIO8080.on('connect', function() {
  console.log('Connected to server on port 8080');
});

socketIO3000.on('connect', function() {
  console.log('Connected to server on port 3000');
});

socketIO8080.on('disconnect', function() {
  console.log('Disconnected from server on port 8080');
});

socketIO3000.on('disconnect', function() {
  console.log('Disconnected from server on port 3000');
});

function sendToServer(event, data, socket) {
  socket.emit(event, data);
}

function readTemperatureHumidity() {
  const { temperature, humidity } = dht.read(DHT_TYPE, GPIO_PIN);
  return { temperature, humidity };
}

function getDecibel(samples) {
  let rms = 0;
  for (let i = 0; i < samples.length; i++) {
    rms += samples[i] * samples[i];
  }
  rms = Math.sqrt(rms / samples.length);

  const decibel = 20 * Math.log10(rms);

  return decibel;
}

function startRecording() {
  const arecord = spawn('arecord', ['-D', 'hw:3,0', '-r', '44100', '-f', 'S16_LE']);

  let isRecording = false;
  let isInitialDetection = true;
  let writer = null;
  let stopswitch = false;
 
  arecord.stdout.on('data', (data) => {
    if (stopswitch) return;
    const samples = new Int16Array(data.buffer, data.byteOffset, data.byteLength / 2);
    const decibel = getDecibel(samples);
    console.log(`Current Decibel: ${decibel.toFixed(2)}dB / Threshold: ${THRESHOLD_DB}dB`);

    if (isRecording) {
      writer.write(data);
    } else {
      if (isInitialDetection) {
        isInitialDetection = false;
        return; // Ignore initial detection
      }

      if (decibel > THRESHOLD_DB) {
        console.log(`Detected sound above ${THRESHOLD_DB}dB. Start recording...`);
        isRecording = true;

        writer = new wav.FileWriter(outputPath, {
          channels: 1,
          sampleRate: 44100,
          bitDepth: 16
        });

        // Play white noise
        const aplay = spawn('aplay', [whiteNoiseFile]);
        aplay.on('error', (error) => {
          console.error('Error occurred while playing white noise:', error);
        });

        setTimeout(() => {
          isRecording = false;
          stopswitch = true;
          arecord.kill();
          console.log('Recording stopped.');
          writer.end();

          // Send the WAV file to the server
          fs.readFile('./recorded.wav', function(err, data) {
              if (err) throw err;
              const base64audio = data.toString('base64');
          sendToServer('audio_data', {'audio_data':base64audio}, socketIO3000);
          });

          // Start a new recording
          setTimeout(() => {
            startRecording();
          }, 1000); // Delay before starting a new recording
        }, RECORDING_DURATION * 1000);
      }
    }
  });
}

// Start recording
startRecording();

// Send temperature and humidity data to the server periodically
setInterval(function() {
  const { temperature, humidity } = readTemperatureHumidity();
  sendToServer('dhtData', { temperature, humidity }, socketIO8080);
}, 2000);
 
