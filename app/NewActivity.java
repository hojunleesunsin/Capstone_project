package com.example.test;

import android.os.Bundle;
import android.view.View;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ImageButton;

import androidx.appcompat.app.AppCompatActivity;

public class NewActivity extends AppCompatActivity {

    private WebView webView;
    private ImageButton backButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.new_activity);

        webView = findViewById(R.id.webview);
        backButton = findViewById(R.id.back_button);

        webView = (WebView) findViewById(R.id.webview);
        webView.setWebViewClient(new WebViewClient());  // Use the built-in WebView browser functionalities
        webView.getSettings().setJavaScriptEnabled(true);  // Enable JavaScript (since your website is using JavaScript)

        webView.loadUrl("http://webview:8080");  // Replace with your server's URL

        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }
}
