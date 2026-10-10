/*
 * TeleLive — Telegram API asosidagi norasmiy ilova.
 * GNU GPL v2 (yoki keyingi) litsenziyasi ostida, Telegram for Android kodi asosida.
 */

package org.telegram.messenger;

import android.content.Context;
import android.content.Intent;
import android.os.Build;

import java.io.PrintWriter;
import java.io.StringWriter;

/**
 * TeleLive'ga xos yordamchi funksiyalar.
 *
 * Telegram tilni serverdan (cloud) yuklab oladi. Ba'zi matnlar — ilova nomi va
 * norasmiy ilova haqidagi ogohlantirish — serverdagi tarjima bilan almashib
 * qolmasligi kerak, shuning uchun ular har doim ilova ichidagi resurslardan olinadi.
 */
public final class TeleLive {

    private TeleLive() {
    }

    public static boolean isLocalOnly(String key, int res) {
        if (res != 0 && (res == R.string.AppName || res == R.string.AppNameBeta || res == R.string.TeleLiveNotice)) {
            return true;
        }
        return "AppName".equals(key) || "AppNameBeta".equals(key) || "TeleLiveNotice".equals(key);
    }

    /**
     * ApplicationLoader.onCreate() ichida, super.onCreate() dan keyin chaqiriladi.
     * true qaytarsa — bu xato oynasi jarayoni, Telegram'ning og'ir ishga tushirilishi o'tkazib yuboriladi.
     */
    public static boolean onApplicationCreate(Context context) {
        if (isCrashProcess()) {
            return true;
        }
        installCrashHandler(context);
        return false;
    }

    private static boolean isCrashProcess() {
        String name = null;
        try {
            if (Build.VERSION.SDK_INT >= 28) {
                name = android.app.Application.getProcessName();
            } else {
                java.io.FileInputStream in = new java.io.FileInputStream("/proc/self/cmdline");
                byte[] buf = new byte[256];
                int n = in.read(buf);
                in.close();
                int len = 0;
                while (len < n && buf[len] != 0) {
                    len++;
                }
                name = new String(buf, 0, len);
            }
        } catch (Throwable ignore) {
        }
        return name != null && name.endsWith(":telelive_crash");
    }

    /**
     * Kutilmagan xatoni ushlab, uni TeleLiveCrashActivity oynasida ko'rsatadi.
     */
    public static void installCrashHandler(final Context context) {
        final Context app = context.getApplicationContext() != null ? context.getApplicationContext() : context;
        final Thread.UncaughtExceptionHandler previous = Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler((thread, error) -> {
            try {
                StringWriter sw = new StringWriter();
                PrintWriter pw = new PrintWriter(sw);
                pw.println("TeleLive " + BuildVars.BUILD_VERSION_STRING
                        + " | Android " + Build.VERSION.RELEASE + " (SDK " + Build.VERSION.SDK_INT + ")"
                        + " | " + Build.MANUFACTURER + " " + Build.MODEL);
                pw.println("Thread: " + thread.getName());
                error.printStackTrace(pw);
                pw.flush();
                String trace = sw.toString();
                if (trace.length() > 60000) {
                    trace = trace.substring(0, 60000);
                }
                Intent intent = new Intent(app, TeleLiveCrashActivity.class);
                intent.putExtra(TeleLiveCrashActivity.EXTRA_TRACE, trace);
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                app.startActivity(intent);
                android.os.Process.killProcess(android.os.Process.myPid());
                System.exit(10);
            } catch (Throwable ignore) {
                if (previous != null) {
                    previous.uncaughtException(thread, error);
                }
            }
        });
    }
}
