package com.example.test;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONObject;

import java.net.URISyntaxException;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;

public class MainActivity extends AppCompatActivity {

    private static final String LOG_TAG = "SocketIO";
    private static final String NODE_SERVER_URL = "http://172.30.1.32:8080";
    private static final String FLASK_SERVER_URL = "http://172.30.1.32:3000";

    private Socket mSocket;
    private Socket pSocket;
    private IO.Options opts;
    private int reconnectAttempts = 0;
    private TextView tvData;
    private int lastReceiveResult = -1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        setupSockets();
        setupUI();
    }

    private void setupSockets() {
        try {
            opts = new IO.Options();
            opts.reconnection = true;
            opts.reconnectionAttempts = 100;
            opts.reconnectionDelay = 5000; // 5 seconds

            mSocket = IO.socket(NODE_SERVER_URL, opts);
            pSocket = IO.socket(FLASK_SERVER_URL, opts);

            mSocket.connect();
            pSocket.connect();

            mSocket.on(Socket.EVENT_CONNECT, onConnect);
            mSocket.on("dhtData", onReceived);
            mSocket.on(Socket.EVENT_DISCONNECT, onDisconnect);

            pSocket.on(Socket.EVENT_CONNECT, onConnect);
            pSocket.on("prediction", onPredictionReceived);
            pSocket.on(Socket.EVENT_DISCONNECT, onDisconnect);

        } catch (URISyntaxException e) {
            Log.e(LOG_TAG, "Invalid URI", e);
        }
    }

    private void setupUI() {
        tvData = findViewById(R.id.TextView);
        Button button1 = findViewById(R.id.button1);
        Button button2 = findViewById(R.id.button2);

        button1.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, NewActivity.class);
            startActivity(intent);
        });

        button2.setOnClickListener(v -> finish());
    }

    private Emitter.Listener onConnect = args -> Log.d(LOG_TAG, "Connected");
    private Emitter.Listener onDisconnect = new Emitter.Listener() {
        @Override
        public void call(Object... args) {
            Log.d(LOG_TAG, "Disconnected");
            reconnectAttempts++;
            if (reconnectAttempts > opts.reconnectionAttempts) {
                runOnUiThread(() -> showCannotConnectAlertAndFinish());
            } else {
                Log.d(LOG_TAG, "Reconnecting...");  // socket.io 라이브러리는 자동으로 재연결을 시도합니다.
            }
        }
    };
    private void showCannotConnectAlertAndFinish() {
        new AlertDialog.Builder(MainActivity.this)
                .setTitle("Connection Error")
                .setMessage("서버와 연결할 수 없습니다.")
                .setPositiveButton(android.R.string.yes, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        finish();
                    }
                })
                .setIcon(R.drawable.ic_launcher_background)
                .show();
    }

    private Emitter.Listener onPredictionReceived = args -> {
        Log.d(LOG_TAG, "Received prediction data");
        JSONObject predictionData = (JSONObject) args[0];
        try {
            final int prediction = predictionData.getInt("prediction");
            if (prediction == 0) {
                runOnUiThread(() -> updateUIBasedOnReceivedData(0));
            }else if (prediction == 1) {
                runOnUiThread(() -> updateUIBasedOnReceivedData(1));
            }
        } catch (Exception e) {
            Log.e(LOG_TAG, "Received non-integer prediction data", e);
        }
    };

    private Emitter.Listener onReceived = args -> {
        Log.d(LOG_TAG, "Received data");
        JSONObject receivedData = (JSONObject) args[0];
        try {
            final int result = receivedData.getInt("dhtData");
            if (result == 0) {
                runOnUiThread(() -> updateUIBasedOnReceivedData(3));
            }else if (result == 1) {
                runOnUiThread(() -> updateUIBasedOnReceivedData(2));
            }
        } catch (Exception e) {
            Log.e(LOG_TAG, "Received non-integer data", e);
        }
    };

    private void updateUIBasedOnReceivedData(int result) {
        if (result == lastReceiveResult) {
            // 결과가 바뀌지 않았으므로 UI 업데이트를 건너뜀
            return;
        }
        lastReceiveResult = result;  // 결과를 저장
        tvData.setText("Recevied: " + result);

        String alertMessage = getAlertMessageBasedOnResult(result);
        if (alertMessage != null && alertMessage != "3") {
            showAlert(alertMessage);
        }
    }

    private String getAlertMessageBasedOnResult(int result) {
        switch (result) {
            case 0:
                return "아기가 이유없이 울어요";
            case 1:
                return "아기가 배고파서 울어요";
            case 2:
                return "아기가 대소변을 눴어요";
            case 3:
                return "3";
            default:
                return null;
        }
    }

    private void showAlert(String message) {
        new AlertDialog.Builder(MainActivity.this)
                .setTitle("Alert")
                .setMessage(message)
                .setPositiveButton(android.R.string.yes, (dialog, which) -> dialog.dismiss())
                .setIcon(R.drawable.ic_launcher_background)
                .show();
    }
}
