/*
 * TeleLive — Telegram API asosidagi norasmiy ilova.
 * GNU GPL v2 (yoki keyingi) litsenziyasi ostida, Telegram for Android kodi asosida.
 */

package org.telegram.messenger;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.util.TypedValue;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

/**
 * Ilova kutilmaganda yopilganda xato matnini ko'rsatadi, uni nusxalab dasturchiga
 * yuborish mumkin. Alohida jarayonda (":telelive_crash") ishlaydi.
 */
public class TeleLiveCrashActivity extends Activity {

    public static final String EXTRA_TRACE = "telelive_trace";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        final String trace = getIntent() != null && getIntent().getStringExtra(EXTRA_TRACE) != null
                ? getIntent().getStringExtra(EXTRA_TRACE) : "";
        int pad = dp(16);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(pad, pad * 2, pad, pad);
        root.setBackgroundColor(Color.rgb(30, 5, 60));

        TextView title = new TextView(this);
        title.setText("TeleLive xato bilan yopildi");
        title.setTextColor(Color.WHITE);
        title.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(title);

        TextView hint = new TextView(this);
        hint.setText("\"Nusxalash\" tugmasini bosing va matnni dasturchiga yuboring.");
        hint.setTextColor(Color.rgb(220, 205, 245));
        hint.setPadding(0, pad / 2, 0, pad);
        root.addView(hint);

        ScrollView scroll = new ScrollView(this);
        TextView body = new TextView(this);
        body.setText(trace);
        body.setTextIsSelectable(true);
        body.setTextColor(Color.rgb(235, 230, 245));
        body.setTypeface(Typeface.MONOSPACE);
        body.setTextSize(TypedValue.COMPLEX_UNIT_SP, 11);
        scroll.addView(body);
        root.addView(scroll, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        Button copy = new Button(this);
        copy.setText("Nusxalash");
        copy.setOnClickListener(v -> {
            try {
                ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                cm.setPrimaryClip(ClipData.newPlainText("TeleLive xato", trace));
                Toast.makeText(this, "Nusxalandi", Toast.LENGTH_SHORT).show();
            } catch (Throwable ignore) {
            }
        });
        root.addView(copy);

        Button close = new Button(this);
        close.setText("Yopish");
        close.setOnClickListener(v -> finish());
        root.addView(close);

        setContentView(root);
    }

    private int dp(int v) {
        return (int) (v * getResources().getDisplayMetrics().density + 0.5f);
    }
}
