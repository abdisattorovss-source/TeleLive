"""TeleLive belgisini (logotipini) chizish.

Belgi: xabar pufagi, ichida uchta "jonli ovoz" chizig'i (teshik ko'rinishida).
Koordinatalar 120x120 birlikdagi to'rda berilgan. Shu fayl yordamida:
  * Android launcher PNG/WebP fayllari (Pillow bilan chiziladi),
  * adaptive icon uchun vector drawable XML,
  * Play Market uchun 512x512 belgi
yaratiladi. Logotipni o'zgartirmoqchi bo'lsangiz, faqat shu fayldagi shakllarni
o'zgartiring.
"""

from PIL import Image, ImageDraw

# --- Shakl (120x120 to'rda) ---
CIRCLE = (62.0, 57.0, 31.0)                     # markaz x, y, radius
TAIL = [(38.0, 70.0), (31.0, 94.0), (58.0, 83.0)]  # pufak dumi
TAIL_ROUND = 2.5                                # dum burchaklarining yumaloqligi
BARS = [(47.0, 50.0, 8.0, 14.0), (58.0, 40.0, 8.0, 34.0), (69.0, 46.0, 8.0, 22.0)]  # x, y, w, h
MARK_BOX = (31.0 - TAIL_ROUND, 26.0, 93.0, 94.0 + TAIL_ROUND)  # chap, yuqori, o'ng, past


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _mark_mask(size, mark_height, ss=4):
    """Belgining oq-qora niqobi (L rejim). mark_height — belgi balandligi pikselda."""
    big = size * ss
    mask = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(mask)
    left, top, right, bottom = MARK_BOX
    k = (mark_height * ss) / (bottom - top)
    cx, cy = (left + right) / 2.0, (top + bottom) / 2.0
    ox, oy = big / 2.0 - cx * k, big / 2.0 - cy * k

    def p(x, y):
        return (ox + x * k, oy + y * k)

    x, y, r = CIRCLE
    d.ellipse([p(x - r, y - r), p(x + r, y + r)], fill=255)
    pts = [p(*pt) for pt in TAIL]
    d.polygon(pts, fill=255)
    d.line(pts + pts[:2], fill=255, width=max(1, int(round(TAIL_ROUND * 2 * k))), joint="curve")
    for bx, by, bw, bh in BARS:
        d.rounded_rectangle([p(bx, by), p(bx + bw, by + bh)], radius=(bw / 2.0) * k, fill=0)
    return mask.resize((size, size), Image.LANCZOS)


def mark_only(size, color, scale):
    """Shaffof fonda faqat belgi. scale — belgi balandligining rasm tomoniga nisbati."""
    mask = _mark_mask(size, size * scale)
    out = Image.new("RGBA", (size, size), hex_rgb(color) + (0,))
    out.putalpha(mask)
    return out


def full_icon(size, bg, fg, round_shape=False, ss=4):
    """Fon + belgi: oddiy launcher belgisi (yumaloq burchakli kvadrat yoki doira)."""
    big = size * ss
    shape = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(shape)
    if round_shape:
        d.ellipse([0, 0, big - 1, big - 1], fill=255)
    else:
        d.rounded_rectangle([0, 0, big - 1, big - 1], radius=big * 26 / 120.0, fill=255)
    shape = shape.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), hex_rgb(bg) + (0,))
    out.putalpha(shape)
    mark = mark_only(size, fg, 0.60 if not round_shape else 0.56)
    out.alpha_composite(mark)
    return out


def solid(size, color):
    return Image.new("RGBA", (size, size), hex_rgb(color) + (255,))


def square_icon(size, bg, fg):
    """Burchaksiz to'liq kvadrat: Play Market 512x512 belgisi (burchakni Play o'zi yumaloqlaydi)."""
    out = solid(size, bg)
    out.alpha_composite(mark_only(size, fg, 0.60))
    return out.convert("RGB")


# --- Vector drawable (adaptive icon foreground / monochrome) ---

def _f(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def _rounded_bar_path(x, y, w, h):
    r = w / 2.0
    return ("M%s,%s a%s,%s 0 0 1 %s,%s v%s a%s,%s 0 0 1 -%s,%s a%s,%s 0 0 1 -%s,-%s v-%s a%s,%s 0 0 1 %s,-%s z" % (
        _f(x + r), _f(y), _f(r), _f(r), _f(r), _f(r), _f(h - 2 * r), _f(r), _f(r), _f(r), _f(r),
        _f(r), _f(r), _f(r), _f(r), _f(h - 2 * r), _f(r), _f(r), _f(r), _f(r)))


def vector_drawable(color, mark_height_dp=54.0):
    """108x108dp adaptive icon uchun vector XML (belgi xavfsiz zona ichida)."""
    left, top, right, bottom = MARK_BOX
    k = mark_height_dp / (bottom - top)
    cx, cy = (left + right) / 2.0, (top + bottom) / 2.0
    tx, ty = 54.0 - cx * k, 54.0 - cy * k
    x, y, r = CIRCLE
    body = "M%s,%s a%s,%s 0 1,0 %s,0 a%s,%s 0 1,0 -%s,0 z " % (
        _f(x - r), _f(y), _f(r), _f(r), _f(2 * r), _f(r), _f(r), _f(2 * r))
    body += " ".join(_rounded_bar_path(*b) for b in BARS)
    tail = "M%s,%s L%s,%s L%s,%s Z" % (TAIL[0] + TAIL[1] + TAIL[2])
    return """<?xml version="1.0" encoding="utf-8"?>
<!-- TeleLive belgisi. scripts/telelive_icons.py tomonidan yaratilgan. -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <group
        android:scaleX="{k}"
        android:scaleY="{k}"
        android:translateX="{tx}"
        android:translateY="{ty}">
        <path
            android:fillColor="{c}"
            android:fillType="evenOdd"
            android:pathData="{body}" />
        <path
            android:fillColor="{c}"
            android:strokeColor="{c}"
            android:strokeWidth="{sw}"
            android:strokeLineJoin="round"
            android:pathData="{tail}" />
    </group>
</vector>
""".format(k=_f(k), tx=_f(tx), ty=_f(ty), c=color, body=body, tail=tail, sw=_f(TAIL_ROUND * 2))


def color_drawable(color):
    return """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="{c}" />
</shape>
""".format(c=color)


def adaptive_icon_xml():
    return """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/telelive_icon_bg" />
    <foreground android:drawable="@drawable/telelive_icon_fg" />
    <monochrome android:drawable="@drawable/telelive_icon_mono" />
</adaptive-icon>
"""


if __name__ == "__main__":
    import json
    import os
    import sys

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg = json.load(open(os.path.join(root, "telelive.json"), encoding="utf-8"))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "branding")
    os.makedirs(out, exist_ok=True)
    square_icon(512, cfg["icon_background"], cfg["icon_foreground"]).save(os.path.join(out, "play_icon_512.png"))
    full_icon(512, cfg["icon_background"], cfg["icon_foreground"]).save(os.path.join(out, "icon_512.png"))
    full_icon(512, cfg["icon_background"], cfg["icon_foreground"], round_shape=True).save(os.path.join(out, "icon_round_512.png"))
    mark_only(512, "#FFFFFF", 0.9).save(os.path.join(out, "mark_white_512.png"))
    mark_only(512, cfg["icon_background"], 0.9).save(os.path.join(out, "mark_dark_512.png"))
    print("Belgilar saqlandi:", out)
