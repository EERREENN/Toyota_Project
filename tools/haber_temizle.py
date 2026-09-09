# -*- coding: utf-8 -*-
"""Haber verisini TEMIZLER. Yalnizca haberleri.

    python tools/haber_temizle.py              # KURU CALISMA: ne silinecegini yazar
    python tools/haber_temizle.py --onayla     # gercekten siler

Kuru calisma varsayilan: bu betik geri alinamaz bir is yapiyor ve
yanlislikla calistirilmasi bir haber arsivini goturur. Silme icin
--onayla vermek gerekiyor.

NEYE DOKUNUR
------------
    news          butun satirlar
    news_image    butun satirlar (zaten CASCADE ile giderdi;
                  yine de acikca siliniyor ki sayisi raporlansin)
    static/uploads/news/    SAHIPSIZ dosyalar

NEYE DOKUNMAZ
-------------
    site_setting      panel sifresi
    login_attempt     giris kilidi
    instance/toyota.db    tasima oncesi CMS arsivi
    static/img/**     depodaki tanitim gorselleri

Son madde onemli: eski ornek haberler gorsellerini
"img/tmmt_img/corolla.jpg" gibi DEPO icindeki yollardan
gosteriyordu. Onlar panel yuklemesi degil, dort tanitim sayfasinin
da kullandigi dosyalar -- silinirlerse TMMT sayfasi bozulurdu.
app/yukleme.py -> panel_yuklenen_mi() bu ayrimi yapiyor ve bu
betik yalnizca uploads/news/ altina bakiyor.

ETIKET / YORUM TABLOSU YOK
--------------------------
Projede haberle iliskili baska tablo bulunmuyor (bkz. app/models.py).
Ileride eklenirse silme sirasi buraya yazilmali.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import text                    # noqa: E402

from app import create_app                     # noqa: E402
from app.extensions import db                  # noqa: E402
from app.models import News, NewsImage         # noqa: E402
from app import yukleme                        # noqa: E402


def _sirayi_sifirla() -> str:
    """Otomatik artan id sayacini sifirlar.

    SQLite'ta sayac iki sekilde tutulur:

      * AUTOINCREMENT verilmisse `sqlite_sequence` tablosunda bir
        satir olarak -- silinmesi gerekir;
      * verilmemisse (bizim durum: SQLAlchemy Integer birincil
        anahtar) ayri bir sayac YOKTUR, yeni id max(rowid)+1
        oldugu icin tablo bosalinca kendiliginden 1'e doner.

    Ikisi de ele aliniyor: sema ileride degisirse betik yine
    dogru davransin.
    """
    var_mi = db.session.execute(text(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name='sqlite_sequence'"
    )).first()
    if not var_mi:
        return "sqlite_sequence yok -- id'ler zaten 1'den baslayacak"

    db.session.execute(text(
        "DELETE FROM sqlite_sequence WHERE name IN ('news', 'news_image')"
    ))
    return "sqlite_sequence sifirlandi"


def main() -> int:
    ayrıştırıcı = argparse.ArgumentParser(description=__doc__)
    ayrıştırıcı.add_argument(
        "--onayla", action="store_true",
        help="gercekten sil (verilmezse yalnizca rapor basar)",
    )
    secenek = ayrıştırıcı.parse_args()
    kuru = not secenek.onayla

    app = create_app()
    with app.app_context():
        haber_adedi = db.session.query(News).count()
        gorsel_adedi = db.session.query(NewsImage).count()

        # Butun haberler silinecegi icin sonrasinda hicbir dosyanin
        # sahibi kalmaz -- bos kume ile soruluyor, yani uploads/news/
        # altindaki HER dosya sahipsiz sayiliyor. Kuru calisma da
        # ayni listeyi basiyor: rapor "silersen ne gider"i gostersin.
        sahipsiz = yukleme.sahipsiz_dosyalar(set())

        print("=" * 60)
        print("KURU CALISMA -- hicbir sey silinmedi" if kuru
              else "SILINIYOR")
        print("=" * 60)
        print(f"  news            : {haber_adedi} satir")
        print(f"  news_image      : {gorsel_adedi} satir")
        print(f"  uploads/news/   : {len(sahipsiz)} sahipsiz dosya")
        for yol in sahipsiz:
            print(f"      - {yol.name}")
        print()
        print("  DOKUNULMAYAN: site_setting, login_attempt, "
              "instance/toyota.db, static/img/**")

        if kuru:
            print()
            print("Silmek icin:  python tools/haber_temizle.py --onayla")
            return 0

        # Once satirlar. news_image acikca siliniyor; ayrica
        # news silinince CASCADE de calisirdi.
        db.session.query(NewsImage).delete()
        db.session.query(News).delete()
        mesaj = _sirayi_sifirla()
        db.session.commit()

        silinen_dosya = 0
        for yol in sahipsiz:
            try:
                yol.unlink()
                silinen_dosya += 1
            except OSError as hata:                      # noqa: PERF203
                print(f"  UYARI: {yol.name} silinemedi ({hata})")

        print()
        print(f"  {haber_adedi} haber, {gorsel_adedi} galeri satiri silindi")
        print(f"  {silinen_dosya} sahipsiz dosya silindi")
        print(f"  {mesaj}")
        print()
        print(f"  kalan haber: {db.session.query(News).count()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
