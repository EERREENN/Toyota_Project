# -*- coding: utf-8 -*-
"""Gelistirme sunucusu.

    python run.py

Yayinda BU DOSYAYI KULLANMA. Bunun yerine:
    waitress-serve --port=8000 "app:create_app()"     # Windows
    gunicorn "app:create_app()"                       # Linux
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
