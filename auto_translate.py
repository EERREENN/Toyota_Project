# -*- coding: utf-8 -*-
"""Otomatik ceviri katmani.

Sablonlardaki tum metinler Turkce yazilir. Ingilizce istendiginde metin
deep-translator (Google) ile cevrilir ve `translations/auto_cache.json`
dosyasina yazilir.

Boylece yeni icerik eklendiginde ayrica ceviri dosyasi tutmaya gerek yok:
ilk goruntulemede otomatik cevrilir, sonra kalici olarak onbellekten
servis edilir. Ceviri alinamazsa (internet yok vb.) metin Turkce
gosterilir; uygulama bu yuzden asla hata vermez.

Onbellegi tamamen doldurmak icin:  python warm_cache.py
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

try:
    from deep_translator import GoogleTranslator
    from deep_translator.exceptions import (
        TranslationNotFound,
        NotValidPayload,
        NotValidLength,
        TooManyRequests,
        RequestError,
        ServerException,
    )
except Exception:  # kutuphane yoksa uygulama yine calissin
    GoogleTranslator = None

    class _Dummy(Exception):
        pass

    TranslationNotFound = NotValidPayload = NotValidLength = _Dummy
    TooManyRequests = RequestError = ServerException = _Dummy

SOURCE_LANG = "tr"
_DIR = Path(__file__).resolve().parent
CACHE_PATH = _DIR / "translations" / "auto_cache.json"

_lock = threading.Lock()
_cache: dict[str, dict[str, str]] = {}

# Basit devre kesici: ust uste cok AG hatasi olursa bir sure denemeyi birak
_fail_count = 0
_pause_until = 0.0
_MAX_FAIL = 6
_PAUSE_SEC = 45.0


def _load() -> None:
    global _cache
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        _cache = data if isinstance(data, dict) else {}
    except (FileNotFoundError, ValueError):
        _cache = {}
    except Exception:
        _cache = {}


def _save() -> None:
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE_PATH.with_name(CACHE_PATH.name + ".tmp")
        tmp.write_text(
            json.dumps(_cache, ensure_ascii=False, indent=1, sort_keys=True),
            encoding="utf-8",
        )
        tmp.replace(CACHE_PATH)
    except Exception:
        pass


_load()


def _remote_translate(text: str, target: str):
    """Ceviri sonucu (str) veya ag hatasinda None dondurur.

    Ceviri bulunamazsa (ozel isim, kisaltma vb.) kaynak metnin kendisi
    dondurulur -> onbellege 'ayni' olarak yazilir, tekrar denenmez.
    """
    global _fail_count, _pause_until
    if GoogleTranslator is None or target == SOURCE_LANG:
        return None
    if time.time() < _pause_until:
        return None

    for deneme in range(2):
        try:
            out = GoogleTranslator(source=SOURCE_LANG, target=target).translate(text)
            _fail_count = 0
            return out or text
        except (TranslationNotFound, NotValidPayload, NotValidLength):
            _fail_count = 0
            return text  # cevrilemez -> kaynak metin
        except (TooManyRequests, ServerException):
            time.sleep(2.0 * (deneme + 1))  # geri cekil, tekrar dene
        except (RequestError, Exception):
            break

    _fail_count += 1
    if _fail_count >= _MAX_FAIL:
        _pause_until = time.time() + _PAUSE_SEC
        _fail_count = 0
    return None


def translate(text, lang: str = "en"):
    """Metni hedef dile cevir (kaynak: Turkce). Kalici onbellekli."""
    if text is None:
        return text
    s = str(text)
    if lang == SOURCE_LANG or not s.strip():
        return text

    bucket = _cache.setdefault(lang, {})
    cached = bucket.get(s)
    if cached is not None:
        return cached

    out = _remote_translate(s, lang)
    if out is None:
        return text  # ag yok -> Turkce goster, sonra tekrar denenir

    with _lock:
        bucket[s] = out
        _save()
    return out


def translate_fresh(text, lang: str = "en"):
    """Onbellegi atlayarak yeniden cevir; basarili olursa onbellege yaz.

    warm_cache.py --refresh tarafindan, kaynakla ayni kalmis (cevrilememis)
    girdileri yeniden denemek icin kullanilir.
    """
    s = str(text)
    if lang == SOURCE_LANG or not s.strip():
        return text
    out = _remote_translate(s, lang)
    if out is None:
        return None
    with _lock:
        _cache.setdefault(lang, {})[s] = out
        _save()
    return out


def pause_remaining() -> float:
    """Devre kesici aciksa kalan saniye (yoksa 0)."""
    return max(0.0, _pause_until - time.time())


def cache_stats() -> dict:
    return {lang: len(d) for lang, d in _cache.items()}
