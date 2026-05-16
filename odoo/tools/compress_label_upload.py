#!/usr/bin/env python3
"""
Сжимает сгенерированные изображения, добавляет подпись с названием товара,
загружает в Odoo filestore + обновляет БД.
"""
import os, sys, base64, hashlib, shutil
import psycopg2
from PIL import Image, ImageDraw, ImageFont

INPUT_DIR  = "/root/pepito/odoo/artifacts/generated_images"
OUTPUT_DIR = "/root/pepito/odoo/artifacts/labeled_images"
FILESTORE  = "/var/lib/containers/storage/volumes/pepito_odoo_odoo_pepito_web_data/_data/.local/share/Odoo/filestore/odoo_user_pepito"

DB_HOST = "10.89.19.2"
DB_PORT = 5432
DB_NAME = "odoo_user_pepito"
DB_USER = "odoo_user_pepito"
DB_PASS = "Db_Pass_Pepito_Z"

MAX_SIZE   = (800, 800)
WEBP_QUAL  = 80

PRODUCT_NAMES = {
    163: "Бычий корень 15см",
    164: "Бычий корень 25см",
    165: "Бычий корень косичка",
    166: "Бычий корень улитка",
    167: "Вымя",
    168: "Вымя кубики 2-3см",
    169: "Вымя палки",
    170: "Калтык кольца",
    171: "Кости",
    172: "Лёгкое",
    173: "Лёгкое брусочки",
    174: "Лёгкое кубики 2-3см",
    175: "Лёгкое кубики 1-2см",
    176: "Лёгкое слайсы",
    177: "Нос говяжий",
    178: "Нос сушёный",
    179: "Носовой хрящ",
    180: "Носовой хрящ сушёный",
    181: "Печень",
    182: "Печень слайсы",
    183: "Рубец",
    184: "Рубец палки",
    185: "Рубец слайсы",
    186: "Смесь",
    187: "Трахея",
    188: "Трахея сушёная",
    189: "Трахея кольца",
    190: "Трахея трубки 15см",
    191: "Уши опалённые",
    192: "Уши сушёные опалённые",
    193: "Фарш",
    194: "Трахея кольца (2)",
    195: "Трахея трубки 15см (2)",
    196: "Трахея сушёная (2)",
    197: "Палочка Яблоня",
    198: "Палочка Груша",
    199: "Палочка Берёза",
    200: "Палочка Вяз",
    201: "Палочка Ольха",
}


def add_label(img: Image.Image, text: str) -> Image.Image:
    draw = ImageDraw.Draw(img)
    w, h = img.size
    font_size = max(14, h // 30)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    # Отступ
    pad = 8
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = w - tw - pad*2, h - th - pad*2

    # Фон под текстом
    draw.rectangle([x - pad, y - pad, w, h], fill=(0, 0, 0, 160))
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    return img


def process_and_upload(product_id: int, name: str):
    src = os.path.join(INPUT_DIR, f"product_{product_id}.jpg")
    if not os.path.exists(src):
        print(f"  [ПРОПУСК] product_{product_id} — файл не найден")
        return False

    out_path = os.path.join(OUTPUT_DIR, f"product_{product_id}.webp")

    # Обработка изображения
    with Image.open(src) as img:
        img = img.convert("RGBA")
        img.thumbnail(MAX_SIZE, Image.LANCZOS)
        img = add_label(img, name)
        img = img.convert("RGB")
        img.save(out_path, "WEBP", quality=WEBP_QUAL, method=6)

    with open(out_path, "rb") as f:
        raw = f.read()

    sha1 = hashlib.sha1(raw).hexdigest()
    store_fname = sha1[:2] + "/" + sha1
    size = len(raw)
    img_b64 = base64.b64encode(raw).decode()

    # Кладём в filestore
    dest_dir = os.path.join(FILESTORE, sha1[:2])
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(out_path, os.path.join(dest_dir, sha1))

    # Обновляем БД
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()

    cur.execute("UPDATE product_template SET image_1920 = %s WHERE id = %s", (img_b64, product_id))

    cur.execute("""
        SELECT id FROM ir_attachment
        WHERE res_model='product.template' AND res_id=%s AND name='image_1920'
    """, (product_id,))
    row = cur.fetchone()

    if row:
        cur.execute("""
            UPDATE ir_attachment
            SET store_fname=%s, file_size=%s, checksum=%s, mimetype='image/webp', db_datas=NULL
            WHERE id=%s
        """, (store_fname, size, sha1, row[0]))
    else:
        cur.execute("""
            INSERT INTO ir_attachment (name, res_model, res_id, store_fname, file_size, checksum, mimetype, type)
            VALUES ('image_1920', 'product.template', %s, %s, %s, %s, 'image/webp', 'binary')
        """, (product_id, store_fname, size, sha1))

    conn.commit()
    conn.close()
    print(f"  [OK] {name} → {size//1024}KB webp, sha1={sha1[:8]}...")
    return True


def process_only(product_id: int, name: str):
    src = os.path.join(INPUT_DIR, f"product_{product_id}.jpg")
    if not os.path.exists(src):
        print(f"  [ПРОПУСК] product_{product_id} — файл не найден")
        return False
    out_path = os.path.join(OUTPUT_DIR, f"product_{product_id}.webp")
    with Image.open(src) as img:
        img = img.convert("RGBA")
        img.thumbnail(MAX_SIZE, Image.LANCZOS)
        img = add_label(img, name)
        img = img.convert("RGB")
        img.save(out_path, "WEBP", quality=WEBP_QUAL, method=6)
    size = os.path.getsize(out_path)
    print(f"  [OK] {name} → {size//1024}KB webp")
    return True


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\n=== Сжатие + подпись ({len(PRODUCT_NAMES)} товаров) ===\n")
    ok = fail = 0
    for pid, name in sorted(PRODUCT_NAMES.items()):
        try:
            if process_only(pid, name):
                ok += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  [ERR] {name}: {e}")
            fail += 1

    print(f"\n=== ИТОГО: {ok} OK, {fail} ошибок ===\n")


if __name__ == "__main__":
    main()
