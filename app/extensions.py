# -*- coding: utf-8 -*-
"""Uygulama genisletmeleri.

Burada sadece nesne olusturulur; uygulamaya baglama create_app() icinde
yapilir. Boylece modeller db'yi import ederken dairesel import olusmaz.
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

# WAL'i acip acmayacagimizi create_app() belirler; event dinleyicisi
# bu bayragi okur.
_wal_acik = False


def wal_ayarla(acik: bool) -> None:
    global _wal_acik
    _wal_acik = bool(acik)


@event.listens_for(Engine, "connect")
def _sqlite_pragmalari(dbapi_baglanti, _baglanti_kaydi):
    """SQLite icin iki onemli ayar.

    foreign_keys: SQLite'ta VARSAYILAN OLARAK KAPALI. Acik olmazsa
        ON DELETE CASCADE calismaz ve silinen blogun ogeleri oksuz kalir.
    journal_mode=WAL: es zamanli okuma performansi. OneDrive/Dropbox gibi
        senkronize klasorlerde sorun cikarabilecegi icin .env'den kontrol
        edilir (SQLITE_WAL).
    """
    if not isinstance(dbapi_baglanti, sqlite3.Connection):
        return
    imlec = dbapi_baglanti.cursor()
    try:
        imlec.execute("PRAGMA foreign_keys=ON")
        if _wal_acik:
            imlec.execute("PRAGMA journal_mode=WAL")
    finally:
        imlec.close()
