/*
 * TeleLive — Telegram API asosidagi norasmiy ilova.
 * GNU GPL v2 (yoki keyingi) litsenziyasi ostida, Telegram for Android kodi asosida.
 */

package org.telegram.messenger;

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
}
