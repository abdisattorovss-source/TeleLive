/*
 * TeleLive — Telegram API asosidagi norasmiy ilova.
 * GNU GPL v2 (yoki keyingi) litsenziyasi ostida, Telegram for Android kodi asosida.
 */

package org.telegram.messenger;

import android.content.Context;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.telegram.ui.Components.LayoutHelper;

/**
 * TeleLive ism vositalari: ism tahrirlash ekraniga qo'shiladigan uslub tugmalari.
 * - Fancy shriftlar (Unicode uslublar) — hamma foydalanuvchiga ko'rinadi.
 * - Yangi O'zbek alifbosiga o'girish (sh->ş, ch->ç, oʻ->ö, gʻ->ğ).
 * - Ism oxiriga emoji qo'shish.
 * Barcha o'zgarishlar firstNameField matniga qo'llanadi; saqlash mavjud "Tayyor" tugmasi orqali.
 */
public final class TeleLiveNameTools {

    private TeleLiveNameTools() {
    }

    // --- Fancy Unicode uslublar ---
    // Har bir uslub: nom, bosh harf bazasi, kichik harf bazasi, raqam bazasi (-1 yo'q), istisnolar.
    private static final Object[][] STYLES = {
            {"𝐀bc", 0x1D400, 0x1D41A, 0x1D7CE, null, null, null},                 // Bold
            {"𝐴bc", 0x1D434, 0x1D44E, -1, null, new int[]{'h', 0x210E}, null},     // Italic
            {"𝑨bc", 0x1D468, 0x1D482, -1, null, null, null},                       // Bold Italic
            {"𝗔bc", 0x1D5D4, 0x1D5EE, 0x1D7EC, null, null, null},                  // Sans Bold
            {"𝙰bc", 0x1D670, 0x1D68A, 0x1D7F6, null, null, null},                  // Monospace
            {"Ａbc", 0xFF21, 0xFF41, 0xFF10, null, null, null},                           // Fullwidth
            {"𝔸bc", 0x1D538, 0x1D552, 0x1D7D8,
                    new int[]{'C', 0x2102, 'H', 0x210D, 'N', 0x2115, 'P', 0x2119, 'Q', 0x211A, 'R', 0x211D, 'Z', 0x2124}, null, null}, // Double-struck
            {"𝒜bc", 0x1D49C, 0x1D4B6, -1,
                    new int[]{'B', 0x212C, 'E', 0x2130, 'F', 0x2131, 'H', 0x210B, 'I', 0x2110, 'L', 0x2112, 'M', 0x2133, 'R', 0x211B},
                    new int[]{'e', 0x212F, 'g', 0x210A, 'o', 0x2134}, null},                  // Script
            {"𝔄bc", 0x1D504, 0x1D51E, -1,
                    new int[]{'C', 0x212D, 'H', 0x210C, 'I', 0x2111, 'R', 0x211C, 'Z', 0x2128}, null, null}, // Fraktur
            {"Ⓐbc", 0x24B6, 0x24D0, -1, null, null,
                    new int[]{'0', 0x24EA, '1', 0x2460, '2', 0x2461, '3', 0x2462, '4', 0x2463, '5', 0x2464, '6', 0x2465, '7', 0x2466, '8', 0x2467, '9', 0x2468}}, // Circled
    };

    private static final String[] EMOJI = {"⭐", "⚽", "🔥", "👑", "🌹", "💜", "❤️", "😎"};

    private static int lookup(int[] ex, char c) {
        if (ex == null) {
            return -1;
        }
        for (int i = 0; i < ex.length; i += 2) {
            if (ex[i] == c) {
                return ex[i + 1];
            }
        }
        return -1;
    }

    private static String applyStyle(String s, int styleIndex) {
        Object[] st = STYLES[styleIndex];
        int bU = (Integer) st[1], bL = (Integer) st[2], bD = (Integer) st[3];
        int[] exU = (int[]) st[4], exL = (int[]) st[5], exD = (int[]) st[6];
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            int cp = -1;
            if (c >= 'A' && c <= 'Z') {
                cp = lookup(exU, c);
                if (cp < 0 && bU > 0) {
                    cp = bU + (c - 'A');
                }
            } else if (c >= 'a' && c <= 'z') {
                cp = lookup(exL, c);
                if (cp < 0 && bL > 0) {
                    cp = bL + (c - 'a');
                }
            } else if (c >= '0' && c <= '9') {
                cp = lookup(exD, c);
                if (cp < 0 && bD > 0) {
                    cp = bD + (c - '0');
                }
            }
            if (cp > 0) {
                out.appendCodePoint(cp);
            } else {
                out.append(c);
            }
        }
        return out.toString();
    }

    private static final String[][] UZ = {
            {"oʻ", "ö"}, {"o‘", "ö"}, {"o'", "ö"},
            {"Oʻ", "Ö"}, {"O‘", "Ö"}, {"O'", "Ö"},
            {"gʻ", "ğ"}, {"g‘", "ğ"}, {"g'", "ğ"},
            {"Gʻ", "Ğ"}, {"G‘", "Ğ"}, {"G'", "Ğ"},
            {"SH", "Ş"}, {"Sh", "Ş"}, {"sh", "ş"},
            {"CH", "Ç"}, {"Ch", "Ç"}, {"ch", "ç"},
    };

    private static String toNewUzbek(String s) {
        for (String[] r : UZ) {
            s = s.replace(r[0], r[1]);
        }
        return s;
    }

    private static TextView chip(Context context, String label, int textColor) {
        TextView tv = new TextView(context);
        tv.setText(label);
        tv.setTextColor(textColor);
        tv.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 15);
        tv.setGravity(Gravity.CENTER);
        int h = AndroidUtilities.dp(10), w = AndroidUtilities.dp(14);
        tv.setPadding(w, h, w, h);
        GradientDrawable bg = new GradientDrawable();
        bg.setCornerRadius(AndroidUtilities.dp(16));
        bg.setColor((textColor & 0x00FFFFFF) | 0x1A000000);
        tv.setBackground(bg);
        return tv;
    }

    /**
     * Ism tahrirlash ekraniga uslub tugmalari qatorini qo'shadi.
     */
    public static void addToolsRow(Context context, LinearLayout parent, final EditText field) {
        try {
            final int textColor = field.getCurrentTextColor();

            TextView hint = new TextView(context);
            hint.setText("TeleLive: ism uslubi");
            hint.setTextColor((textColor & 0x00FFFFFF) | 0x80000000);
            hint.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 13);
            hint.setPadding(AndroidUtilities.dp(24), AndroidUtilities.dp(14), AndroidUtilities.dp(24), AndroidUtilities.dp(6));
            parent.addView(hint, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, LayoutHelper.WRAP_CONTENT));

            LinearLayout row = new LinearLayout(context);
            row.setOrientation(LinearLayout.HORIZONTAL);

            final String base = field.getText() != null && field.getText().length() > 0
                    ? field.getText().toString() : "Namuna";

            TextView uz = chip(context, "🇺🇿 Yangi alifbo", textColor);
            uz.setOnClickListener(new View.OnClickListener() {
                public void onClick(View v) {
                    apply(field, toNewUzbek(current(field)));
                }
            });
            row.addView(uz, chipParams());

            for (int i = 0; i < STYLES.length; i++) {
                final int idx = i;
                String preview = applyStyle("Ab", i);
                TextView c = chip(context, preview, textColor);
                c.setOnClickListener(new View.OnClickListener() {
                    public void onClick(View v) {
                        apply(field, applyStyle(current(field), idx));
                    }
                });
                row.addView(c, chipParams());
            }

            for (final String e : EMOJI) {
                TextView c = chip(context, e, textColor);
                c.setOnClickListener(new View.OnClickListener() {
                    public void onClick(View v) {
                        apply(field, current(field) + " " + e);
                    }
                });
                row.addView(c, chipParams());
            }

            HorizontalScrollView scroll = new HorizontalScrollView(context);
            scroll.setHorizontalScrollBarEnabled(false);
            scroll.addView(row, new LinearLayout.LayoutParams(LayoutHelper.WRAP_CONTENT, LayoutHelper.WRAP_CONTENT));
            scroll.setPadding(AndroidUtilities.dp(18), 0, AndroidUtilities.dp(18), AndroidUtilities.dp(8));
            scroll.setClipToPadding(false);
            parent.addView(scroll, LayoutHelper.createLinear(LayoutHelper.MATCH_PARENT, LayoutHelper.WRAP_CONTENT));
        } catch (Throwable ignore) {
        }
    }

    private static LinearLayout.LayoutParams chipParams() {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(LayoutHelper.WRAP_CONTENT, LayoutHelper.WRAP_CONTENT);
        p.rightMargin = AndroidUtilities.dp(8);
        return p;
    }

    private static String current(EditText field) {
        return field.getText() != null ? field.getText().toString() : "";
    }

    private static void apply(EditText field, String value) {
        field.setText(value);
        field.setSelection(field.length());
    }
}
