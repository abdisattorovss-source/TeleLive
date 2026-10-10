"""TeleLive belgisini (logotipini) tayyorlash.

Manba: branding/logo_mark.webp — foydalanuvchi bergan logotipdagi samolyotcha belgisi,
shaffof fonda (fon olib tashlangan). Shu belgidan:
  * Android launcher PNG/WebP fayllari,
  * adaptive icon (fon + belgi + monoxrom),
  * bildirishnoma belgisi (oq siluet),
  * kirish ekranidagi animatsiya teksturasi,
  * Play Market uchun 512x512 belgi
yaratiladi. Logotipni almashtirish uchun branding/logo_mark.webp faylini almashtiring
(shaffof fonli PNG/WebP), ranglarni telelive.json da o'zgartiring.
"""

import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK_PATH = os.path.join(ROOT, "branding", "logo_mark.webp")
MARK_B64_PATH = MARK_PATH + ".b64"  # GitHub'ga matn sifatida yuklash uchun base64 nusxa

_mark_cache = None


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def load_mark():
    global _mark_cache
    if _mark_cache is None:
        if os.path.exists(MARK_PATH):
            _mark_cache = Image.open(MARK_PATH).convert("RGBA")
        else:
            import base64
            import io
            with open(MARK_B64_PATH, encoding="ascii") as f:
                data = base64.b64decode("".join(f.read().split()))
            _mark_cache = Image.open(io.BytesIO(data)).convert("RGBA")
    return _mark_cache


def fit_mark(size, scale, color=None):
    """size x size shaffof rasm, markazida belgi. scale — belgi eni/rasm eni nisbati.
    color berilsa, belgi shu rangdagi siluetga aylanadi (bildirishnoma, monoxrom)."""
    mark = load_mark()
    w = max(1, int(round(size * scale)))
    h = max(1, int(round(mark.height * w / mark.width)))
    if h > size * scale:
        h = max(1, int(round(size * scale)))
        w = max(1, int(round(mark.width * h / mark.height)))
    m = mark.resize((w, h), Image.LANCZOS)
    if color is not None:
        sil = Image.new("RGBA", m.size, hex_rgb(color) + (255,))
        sil.putalpha(m.getchannel("A"))
        m = sil
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(m, ((size - w) // 2, (size - h) // 2))
    return out


def gradient(size, center, edge):
    """Logotipdagi kabi radial binafsha fon (markaz yuqoriroqda)."""
    c, e = hex_rgb(center), hex_rgb(edge)
    small = 64
    img = Image.new("RGB", (small, small))
    px = img.load()
    cx, cy = small / 2.0, small * 0.38
    rmax = ((small / 2.0) ** 2 + (small * 0.62) ** 2) ** 0.5
    for y in range(small):
        for x in range(small):
            t = min(1.0, (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) / rmax)
            px[x, y] = tuple(int(c[i] + (e[i] - c[i]) * t) for i in range(3))
    return img.resize((size, size), Image.BICUBIC).convert("RGBA")


def _shape_mask(size, round_shape, ss=4):
    big = size * ss
    shape = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(shape)
    if round_shape:
        d.ellipse([0, 0, big - 1, big - 1], fill=255)
    else:
        d.rounded_rectangle([0, 0, big - 1, big - 1], radius=big * 26 / 120.0, fill=255)
    return shape.resize((size, size), Image.LANCZOS)


def full_icon(size, cfg, round_shape=False):
    """Fon + belgi: oddiy launcher belgisi (yumaloq burchakli kvadrat yoki doira)."""
    out = gradient(size, cfg["icon_gradient_center"], cfg["icon_gradient_edge"])
    out.alpha_composite(fit_mark(size, 0.70 if not round_shape else 0.62))
    out.putalpha(_shape_mask(size, round_shape))
    return out


def square_icon(size, cfg):
    """Burchaksiz to'liq kvadrat: Play Market 512x512 belgisi."""
    out = gradient(size, cfg["icon_gradient_center"], cfg["icon_gradient_edge"])
    out.alpha_composite(fit_mark(size, 0.70))
    return out.convert("RGB")


def adaptive_foreground(size):
    """108dp adaptive icon foreground: belgi markaziy 66dp xavfsiz zona ichida."""
    return fit_mark(size, 0.56)


def adaptive_monochrome(size):
    return fit_mark(size, 0.56, color="#FFFFFF")


def notification_icon(size):
    return fit_mark(size, 0.96, color="#FFFFFF")


def intro_plane(width, height):
    """Kirish ekranidagi animatsiya teksturasi (asl Telegram samolyotchasi o'rniga)."""
    mark = load_mark()
    k = min(width / mark.width, height / mark.height) * 0.92
    m = mark.resize((max(1, int(mark.width * k)), max(1, int(mark.height * k))), Image.LANCZOS)
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    out.alpha_composite(m, ((width - m.width) // 2, (height - m.height) // 2))
    return out


def solid(size, color):
    return Image.new("RGBA", (size, size), hex_rgb(color) + (255,))


def gradient_drawable(center, edge):
    return """<?xml version="1.0" encoding="utf-8"?>
<!-- TeleLive belgisi foni. scripts/telelive_icons.py tomonidan yaratilgan. -->
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient
        android:type="radial"
        android:centerX="0.5"
        android:centerY="0.38"
        android:gradientRadius="80dp"
        android:startColor="{c}"
        android:endColor="{e}" />
</shape>
""".format(c=center, e=edge)


def adaptive_icon_xml():
    return """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/telelive_icon_bg" />
    <foreground android:drawable="@mipmap/telelive_icon_fg" />
    <monochrome android:drawable="@mipmap/telelive_icon_mono" />
</adaptive-icon>
"""


if __name__ == "__main__":
    import json
    import sys

    cfg = json.load(open(os.path.join(ROOT, "telelive.json"), encoding="utf-8"))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "branding")
    os.makedirs(out, exist_ok=True)
    square_icon(512, cfg).save(os.path.join(out, "play_icon_512.png"))
    full_icon(512, cfg).save(os.path.join(out, "icon_512.png"))
    full_icon(512, cfg, round_shape=True).save(os.path.join(out, "icon_round_512.png"))
    notification_icon(256).save(os.path.join(out, "notification_256.png"))
    print("Belgilar saqlandi:", out)
