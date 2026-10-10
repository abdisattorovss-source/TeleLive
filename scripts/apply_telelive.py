#!/usr/bin/env python3
"""Telegram for Android manba kodini TeleLive'ga aylantiradi.

Ishlatilishi:
    python3 scripts/apply_telelive.py --tg <Telegram kodi papkasi> [--abi arm64|all]

Kerakli muhit o'zgaruvchilari (GitHub Secrets'dan keladi):
    TELEGRAM_API_ID, TELEGRAM_API_HASH     — my.telegram.org dan olinadi (majburiy)
    GOOGLE_SERVICES_JSON                    — Firebase fayli (ixtiyoriy; bo'lmasa push ishlamaydi)
    KEYSTORE_BASE64, KEYSTORE_PASSWORD,
    KEY_ALIAS, KEY_PASSWORD                 — imzolash kaliti (Play uchun majburiy, sinov uchun ixtiyoriy)

Har bir o'zgarish aniq tekshiriladi: Telegram kodi yangilanib, kerakli qator topilmasa,
skript xato bilan to'xtaydi (jim o'tib ketmaydi).
"""

import argparse
import base64
import json
import os
import re
import shutil
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import telelive_icons as icons  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PatchError(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def sub_once(path, pattern, repl, flags=0, count=1, label=None):
    text = read(path)
    new, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n == 0:
        raise PatchError("Topilmadi: %s\n  fayl: %s\n  qidiruv: %s" % (label or "", path, pattern))
    write(path, new)
    print("  ✓ %s" % (label or pattern))


def java_str(value):
    return value.replace("\\", "\\\\").replace("\"", "\\\"")


def xml_str(value):
    return value.replace("&", "&amp;").replace("<", "&lt;").replace("'", "\\'")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tg", required=True, help="Telegram for Android kodi joylashgan papka")
    ap.add_argument("--abi", choices=["arm64", "all"], default="all")
    ap.add_argument("--allow-missing-api", action="store_true",
                    help="Faqat skriptni sinash uchun: API ID bo'lmasa ham davom etadi")
    args = ap.parse_args()

    cfg = json.load(open(os.path.join(ROOT, "telelive.json"), encoding="utf-8"))
    tg = os.path.abspath(args.tg)
    proj = os.path.join(tg, "TMessagesProj")
    app = os.path.join(tg, "TMessagesProj_App")
    java = os.path.join(proj, "src", "main", "java", "org", "telegram")
    res = os.path.join(proj, "src", "main", "res")
    name = cfg["app_name"]

    api_id = os.environ.get("TELEGRAM_API_ID", "").strip()
    api_hash = os.environ.get("TELEGRAM_API_HASH", "").strip()
    if not api_id or not api_hash:
        if not args.allow_missing_api:
            raise PatchError("TELEGRAM_API_ID va TELEGRAM_API_HASH berilmagan. "
                             "Ularni my.telegram.org dan olib, GitHub Secrets'ga qo'shing.")
        api_id, api_hash = "0", "TEST_ONLY_NOT_FOR_RELEASE"
    elif not api_id.isdigit() or not re.fullmatch(r"[0-9a-fA-F]{32}", api_hash):
        raise PatchError("TELEGRAM_API_ID raqam, TELEGRAM_API_HASH esa 32 belgili bo'lishi kerak.")

    print("1. Paket nomi va versiya")
    gp = os.path.join(tg, "gradle.properties")
    sub_once(gp, r"(?m)^APP_PACKAGE=.*$", "APP_PACKAGE=" + cfg["package"], label="APP_PACKAGE")
    sub_once(gp, r"(?m)^APP_VERSION_NAME=.*$", "APP_VERSION_NAME=" + cfg["version_name"], label="APP_VERSION_NAME")
    sub_once(gp, r"(?m)^APP_VERSION_CODE=.*$", "APP_VERSION_CODE=" + str(cfg["version_code"]), label="APP_VERSION_CODE")
    # GitHub'ning bepul serverida 16 GB xotira bor
    sub_once(gp, r"(?m)^org\.gradle\.jvmargs=.*$", "org.gradle.jvmargs=-Xmx6g -XX:MaxMetaspaceSize=1g", label="Gradle xotirasi")

    print("2. Faqat asosiy ilova modulini qoldirish")
    st = os.path.join(tg, "settings.gradle")
    for module in ("TMessagesProj_AppHuawei", "TMessagesProj_AppHockeyApp",
                   "TMessagesProj_AppStandalone", "TMessagesProj_AppTests"):
        sub_once(st, r"(?m)^include ':%s'\s*\n" % module, "", label="olib tashlandi: " + module)

    print("3. BuildVars: API kalitlari va Telegram'ga xos sozlamalar")
    bv = os.path.join(java, "messenger", "BuildVars.java")
    sub_once(bv, r"public static int APP_ID = \d+;", "public static int APP_ID = %s;" % api_id, label="APP_ID")
    sub_once(bv, r"public static String APP_HASH = \"[^\"]*\";",
             "public static String APP_HASH = \"%s\";" % java_str(api_hash), label="APP_HASH")
    sub_once(bv, r"public static String SAFETYNET_KEY = \"[^\"]*\";",
             "public static String SAFETYNET_KEY = \"\";", label="SAFETYNET_KEY (Telegram'niki o'chirildi)")
    sub_once(bv, r"public static String PLAYSTORE_APP_URL = \"[^\"]*\";",
             "public static String PLAYSTORE_APP_URL = \"https://play.google.com/store/apps/details?id=%s\";" % cfg["package"],
             label="PLAYSTORE_APP_URL")
    sub_once(bv, r"public static String GOOGLE_AUTH_CLIENT_ID = \"[^\"]*\";",
             "public static String GOOGLE_AUTH_CLIENT_ID = \"\";", label="GOOGLE_AUTH_CLIENT_ID")
    sub_once(bv, r"public static boolean IS_BILLING_UNAVAILABLE = (true|false);",
             "public static boolean IS_BILLING_UNAVAILABLE = true;",
             label="Google Play to'lovi o'chirildi (Premium @PremiumBot orqali olinadi)")
    sub_once(bv, r"public static boolean SUPPORTS_PASSKEYS = (true|false);",
             "public static boolean SUPPORTS_PASSKEYS = false;", label="SUPPORTS_PASSKEYS")
    sub_once(bv, r"public static boolean CHECK_UPDATES = (true|false);",
             "public static boolean CHECK_UPDATES = false;", label="Telegram yangilanish tekshiruvi o'chirildi")

    print("4. Akkauntlar soni")
    n = int(cfg["max_accounts"])
    uc = os.path.join(java, "messenger", "UserConfig.java")
    sub_once(uc, r"public final static int MAX_ACCOUNT_COUNT = \d+;",
             "public final static int MAX_ACCOUNT_COUNT = %d;" % n, label="MAX_ACCOUNT_COUNT = %d" % n)
    sub_once(uc, r"public static int getMaxAccountCount\(\) \{\s*return [^;]+;",
             "public static int getMaxAccountCount() {\n        return MAX_ACCOUNT_COUNT;", label="getMaxAccountCount")
    defines = os.path.join(proj, "jni", "tgnet", "Defines.h")
    sub_once(defines, r"#define MAX_ACCOUNT_COUNT \d+", "#define MAX_ACCOUNT_COUNT %d" % (n + 1),
             label="native MAX_ACCOUNT_COUNT = %d" % (n + 1))

    print("5. Ilova nomi")
    for d in sorted(os.listdir(res)):
        f = os.path.join(res, d, "strings.xml")
        if d.startswith("values") and os.path.isfile(f) and 'name="AppName"' in read(f):
            sub_once(f, r'<string name="AppName">[^<]*</string>',
                     '<string name="AppName">%s</string>' % xml_str(name), label="%s/AppName" % d)
            sub_once(f, r'<string name="AppNameBeta">[^<]*</string>',
                     '<string name="AppNameBeta">%s Beta</string>' % xml_str(name), label="%s/AppNameBeta" % d)

    print("6. TeleLive fayllari (overlay)")
    overlay = os.path.join(ROOT, "overlay")
    shutil.copy(os.path.join(overlay, "java", "org", "telegram", "messenger", "TeleLive.java"),
                os.path.join(java, "messenger", "TeleLive.java"))
    for d in os.listdir(os.path.join(overlay, "res")):
        os.makedirs(os.path.join(res, d), exist_ok=True)
        shutil.copy(os.path.join(overlay, "res", d, "telelive_strings.xml"),
                    os.path.join(res, d, "telelive_strings.xml"))
    print("  ✓ TeleLive.java va uz/ru/en matnlar")

    lc = os.path.join(java, "messenger", "LocaleController.java")
    sub_once(lc,
             r"(private String getStringV2\(String key, @StringRes int stringRes, String fallback\) \{\s*"
             r"final Context context = ApplicationLoader\.applicationContext;\s*String value;\n)",
             r"\1\n        if (TeleLive.isLocalOnly(key, stringRes)) {\n"
             r"            checkLocalizationInternal();\n"
             r"            value = localizationInternal.getByResNameOrResId(context, key, stringRes);\n"
             r"            if (value != null) {\n                return value;\n            }\n        }\n",
             label="Ilova nomi serverdagi tarjima bilan almashmaydi")

    intro = os.path.join(java, "ui", "IntroActivity.java")
    sub_once(intro, r"LocaleController\.getString\(R\.string\.Page1Message\),",
             "LocaleController.getString(R.string.Page1Message) + \"\\\\n\\\\n\" + "
             "LocaleController.getString(R.string.TeleLiveNotice),",
             label="Kirish sahifasida norasmiy ilova haqida yozuv")

    print("7. Tillar va arxitektura")
    ab = os.path.join(app, "build.gradle")
    sub_once(ab, r'localeFilters \+= \["zz"\]', 'localeFilters += ["zz", "uz", "ru"]', label="uz va ru resurslari")
    if args.abi == "arm64":
        sub_once(ab,
                 r'(\n        afat \{\s*ndk \{\s*abiFilters )"armeabi-v7a", "arm64-v8a", "x86", "x86_64"',
                 r'\1"arm64-v8a"', label="faqat arm64 (tezroq sinov yig'imi)")

    print("8. Firebase (google-services.json)")
    gs_path = os.path.join(app, "google-services.json")
    gs = os.environ.get("GOOGLE_SERVICES_JSON", "").strip()
    if gs:
        if not gs.startswith("{"):
            gs = base64.b64decode(gs).decode("utf-8")
        data = json.loads(gs)
        pkgs = [c["client_info"]["android_client_info"]["package_name"] for c in data.get("client", [])]
        if cfg["package"] not in pkgs:
            raise PatchError("google-services.json ichida %s paketi yo'q (bor: %s). Firebase'da shu nomli "
                             "Android ilova qo'shing." % (cfg["package"], ", ".join(pkgs)))
        write(gs_path, gs)
        print("  ✓ Firebase fayli qo'yildi")
    else:
        dummy = {
            "project_info": {"project_number": "000000000000", "project_id": "telelive-no-firebase",
                             "storage_bucket": "telelive-no-firebase.appspot.com"},
            "client": [{
                "client_info": {"mobilesdk_app_id": "1:000000000000:android:0000000000000000",
                                "android_client_info": {"package_name": cfg["package"]}},
                "oauth_client": [],
                "api_key": [{"current_key": "AIzaSyA-NO-FIREBASE-00000000000000000"}],
                "services": {"appinvite_service": {"other_platform_oauth_client": []}},
            }],
            "configuration_version": "1",
        }
        write(gs_path, json.dumps(dummy, indent=2))
        print("  ! Firebase berilmagan: ilova ishlaydi, lekin push-bildirishnomalar kelmaydi")

    print("9. Imzolash kaliti")
    ks = os.environ.get("KEYSTORE_BASE64", "").strip()
    if ks:
        with open(os.path.join(proj, "config", "release.keystore"), "wb") as f:
            f.write(base64.b64decode(ks))
        sub_once(gp, r"(?m)^RELEASE_KEY_PASSWORD=.*$", "RELEASE_KEY_PASSWORD=" + os.environ["KEY_PASSWORD"], label="kalit paroli")
        sub_once(gp, r"(?m)^RELEASE_KEY_ALIAS=.*$", "RELEASE_KEY_ALIAS=" + os.environ["KEY_ALIAS"], label="kalit nomi")
        sub_once(gp, r"(?m)^RELEASE_STORE_PASSWORD=.*$", "RELEASE_STORE_PASSWORD=" + os.environ["KEYSTORE_PASSWORD"], label="keystore paroli")
    else:
        print("  ! O'z kalitingiz berilmagan: sinov kaliti ishlatiladi (Play Market'ga yuklab bo'lmaydi)")

    print("10. Belgilar (logotip)")
    replace_icons(res, cfg)
    print("\nTayyor: TeleLive o'zgarishlari qo'llandi.")


def replace_icons(res, cfg):
    bg, fg = cfg["icon_background"], cfg["icon_foreground"]
    draw = os.path.join(res, "drawable")
    write(os.path.join(draw, "telelive_icon_bg.xml"), icons.color_drawable(bg))
    write(os.path.join(draw, "telelive_icon_fg.xml"), icons.vector_drawable(fg))
    write(os.path.join(draw, "telelive_icon_mono.xml"), icons.vector_drawable("#FFFFFF"))
    # Telegram samolyotchasi ilovaning boshqa joylarida ham monoxrom belgi sifatida ishlatiladi
    write(os.path.join(draw, "icon_plane.xml"), icons.vector_drawable("#FFFFFF"))

    count = 0
    anydpi = os.path.join(res, "mipmap-anydpi-v26")
    for f in os.listdir(anydpi):
        if f.endswith(".xml"):
            write(os.path.join(anydpi, f), icons.adaptive_icon_xml())
            count += 1

    for d in sorted(os.listdir(res)):
        if not (d.startswith("mipmap") or d.startswith("drawable")):
            continue
        for f in sorted(os.listdir(os.path.join(res, d))):
            base, ext = os.path.splitext(f)
            if ext not in (".png", ".webp"):
                continue
            path = os.path.join(res, d, f)
            if base == "notification":
                img = None
            elif "launcher" in base:
                img = "launcher"
            elif "foreground" in base:
                img = "foreground"
            elif "background_clip" in base or base.endswith("background_sa"):
                img = "background"
            else:
                continue
            with Image.open(path) as im:
                size = im.size[0]
            if base == "notification":
                out = icons.mark_only(size, "#FFFFFF", 0.92)
            elif img == "launcher":
                out = icons.full_icon(size, bg, fg, round_shape="round" in base)
            elif img == "foreground":
                out = icons.mark_only(size, fg, 0.50)
            else:
                out = icons.solid(size, bg)
            if ext == ".webp":
                out.save(path, "WEBP", lossless=True)
            else:
                out.save(path, "PNG")
            count += 1
    print("  ✓ %d ta belgi fayli almashtirildi" % count)


if __name__ == "__main__":
    try:
        main()
    except PatchError as e:
        print("\nXATO: %s" % e, file=sys.stderr)
        sys.exit(1)
