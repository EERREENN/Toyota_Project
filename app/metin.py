# -*- coding: utf-8 -*-
"""Metin yardimcilari."""

from __future__ import annotations

from typing import Any

# Turkce harfleri ASCII karsiliklarina indirger. Sozluk aramasi
# "sogut" yazinca "söğüt"u de bulsun diye; ayni donusum tarayici
# tarafinda da var (static/js/modules/glossary.js) -- ikisi ayrisirsa
# arama sessizce eksik sonuc dondurur, o yuzden birlikte degistirin.
#
# NOT: once translate(), sonra lower(). Ters sirada "İ".lower() ayri
# bir birlestirici nokta uretir ("i̇") ve eslesme bozulur.
_SADE_HARFLER = str.maketrans({
    "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g",
    "ı": "i", "I": "i", "İ": "i",
    "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
    "â": "a", "Â": "a", "î": "i", "Î": "i", "û": "u", "Û": "u",
})


def sadelestir(metin: Any) -> str:
    """'Genchi Genbutsu' / 'İsraf' -> aramada karsilastirilabilir hal.

    Sozluk sablonu bunu `data-arama` ozniteligine basar; tarayici
    tarafi her tusta yeniden normalize etmek zorunda kalmaz.
    """
    if not metin:
        return ""
    return str(metin).translate(_SADE_HARFLER).lower()
