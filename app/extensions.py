# -*- coding: utf-8 -*-
"""Uygulama genisletmeleri.

Burada sadece nesne olusturulur; uygulamaya baglama create_app() icinde
yapilir. Boylece modeller db'yi import ederken dairesel import olusmaz.

NOT -- veritabani YALNIZCA haberler icin:
Dort tanitim sayfasi (TMMT, Global Toyota, TPS, Cevre) veritabanina hic
dokunmaz; icerikleri templates/pages/*.html icinde duruyor. Veritabani
dosyasi silinse bile o sayfalar calismaya devam eder.
"""

from __future__ import annotations

import sqlite3

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 tarzi taban sinif (Mapped / mapped_column icin)."""


db = SQLAlchemy(model_class=Base)


@event.listens_for(Engine, "connect")
def _sqlite_pragmalari(dbapi_baglanti, _baglanti_kaydi):
    """SQLite'ta yabanci anahtarlar VARSAYILAN OLARAK KAPALIDIR.

    Simdilik tek tablo var, ama iliskili bir tablo eklendiginde
    ON DELETE kurallarinin calismasi icin bu satir gerekli; sonradan
    fark edilmesi zor bir hata olurdu.
    """
    if not isinstance(dbapi_baglanti, sqlite3.Connection):
        return
    imlec = dbapi_baglanti.cursor()
    try:
        imlec.execute("PRAGMA foreign_keys=ON")
    finally:
        imlec.close()
