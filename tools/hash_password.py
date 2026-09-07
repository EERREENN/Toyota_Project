# -*- coding: utf-8 -*-
"""Panel sifresi icin hash uretir.

Ciktisini .env dosyasindaki ADMIN_PASSWORD_HASH satirina yapistir.
Duz sifre hicbir yerde saklanmaz.

    python tools/hash_password.py                 # sifreyi gizli sorar
    python tools/hash_password.py --parola "..."  # betikten kullanmak icin

Ayrica gizli panel adresi ve oturum anahtari uretmeye yarayan
kisayollar:

    python tools/hash_password.py --anahtar       # FLASK_SECRET_KEY uret
    python tools/hash_password.py --yol           # ADMIN_PATH uret
"""

from __future__ import annotations

import argparse
import getpass
import secrets
import sys

from werkzeug.security import generate_password_hash

EN_AZ_UZUNLUK = 8


def parola_al(verilen: str | None) -> str:
    if verilen:
        return verilen
    ilk = getpass.getpass("Yeni panel sifresi: ")
    ikinci = getpass.getpass("Tekrar: ")
    if ilk != ikinci:
        print("Sifreler eslesmiyor.", file=sys.stderr)
        raise SystemExit(1)
    return ilk


def main() -> int:
    p = argparse.ArgumentParser(description="Panel sifresi hash'i uret")
    p.add_argument("--parola", help="sifreyi dogrudan ver (sormadan)")
    p.add_argument("--anahtar", action="store_true", help="FLASK_SECRET_KEY uret")
    p.add_argument("--yol", action="store_true", help="ADMIN_PATH uret")
    a = p.parse_args()

    if a.anahtar:
        print(f"FLASK_SECRET_KEY={secrets.token_urlsafe(48)}")
        return 0

    if a.yol:
        print(f"ADMIN_PATH=/panel-{secrets.token_hex(4)}")
        return 0

    parola = parola_al(a.parola)
    if len(parola) < EN_AZ_UZUNLUK:
        print(
            f"Sifre en az {EN_AZ_UZUNLUK} karakter olmali "
            f"(verilen: {len(parola)}).",
            file=sys.stderr,
        )
        return 1

    # scrypt: werkzeug'un varsayilani, yavas ve tuzlu -- kaba kuvvete dayanikli
    ozet = generate_password_hash(parola, method="scrypt")

    print()
    print("Asagidaki satiri .env dosyana yapistir:")
    print()
    print(f"ADMIN_PASSWORD_HASH={ozet}")
    print()
    print("Not: duz sifreyi .env'ye YAZMA. Bu hash'ten geri elde edilemez.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
