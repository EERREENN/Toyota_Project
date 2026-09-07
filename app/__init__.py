# -*- coding: utf-8 -*-
"""Toyota tanitim sitesi + icerik yonetim sistemi."""

from __future__ import annotations

from .extensions import db
from .factory import create_app

__all__ = ["db", "create_app"]
