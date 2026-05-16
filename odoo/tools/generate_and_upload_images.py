#!/usr/bin/env python3
"""
Генерирует изображения для всех товаров pepito через pollinations.ai
и загружает их напрямую в Odoo через psycopg2.
"""
import os, sys, time, base64, urllib.request, urllib.parse, hashlib
import psycopg2

DB_HOST = "10.89.19.2"
DB_PORT = 5432
DB_NAME = "odoo_user_pepito"
DB_USER = "odoo_user_pepito"
DB_PASS = "Db_Pass_Pepito_Z"

OUTPUT_DIR = "/root/pepito/odoo/artifacts/generated_images"

PRODUCTS = {
    163: ("Бычий корень 15см", "dried beef pizzle stick 15cm natural dog treat, food photography, white background, product photo"),
    164: ("Бычий корень 25см", "dried beef pizzle stick 25cm natural dog treat, food photography, white background, product photo"),
    165: ("Бычий корень косичка", "dried beef pizzle braid twisted natural dog treat, food photography, white background, product photo"),
    166: ("Бычий корень улитка", "dried beef pizzle coiled snail shape natural dog treat, food photography, white background, product photo"),
    167: ("Вымя", "dried beef udder natural dog treat chunks, food photography, white background, product photo"),
    168: ("Вымя кубики 2-3см", "dried beef udder cubes 2-3cm natural dog treat, food photography, white background, product photo"),
    169: ("Вымя палки", "dried beef udder sticks natural dog treat, food photography, white background, product photo"),
    170: ("Калтык кольца", "dried beef larynx rings natural dog treat, food photography, white background, product photo"),
    171: ("Кости", "dried beef bones natural dog treat variety, food photography, white background, product photo"),
    172: ("Лёгкое", "dried beef lung natural dog treat, food photography, white background, product photo"),
    173: ("Лёгкое брусочки", "dried beef lung strips natural dog treat, food photography, white background, product photo"),
    174: ("Лёгкое кубики 2-3см", "dried beef lung cubes 2-3cm natural dog treat, food photography, white background, product photo"),
    175: ("Лёгкое кубики 1-2см", "dried beef lung small cubes 1-2cm natural dog treat, food photography, white background, product photo"),
    176: ("Лёгкое слайсы", "dried beef lung slices thin natural dog treat, food photography, white background, product photo"),
    177: ("Нос говяжий", "dried beef nose natural dog treat whole, food photography, white background, product photo"),
    178: ("Нос сушёный", "dried beef nose dehydrated natural dog treat, food photography, white background, product photo"),
    179: ("Носовой хрящ", "dried beef nasal cartilage natural dog treat, food photography, white background, product photo"),
    180: ("Носовой хрящ сушёный", "dried beef nasal cartilage dehydrated natural dog treat, food photography, white background, product photo"),
    181: ("Печень", "dried beef liver natural dog treat, food photography, white background, product photo"),
    182: ("Печень слайсы", "dried beef liver slices thin dehydrated natural dog treat, food photography, white background, product photo"),
    183: ("Рубец", "dried beef tripe natural dog treat, food photography, white background, product photo"),
    184: ("Рубец палки", "dried beef tripe sticks natural dog treat, food photography, white background, product photo"),
    185: ("Рубец слайсы", "dried beef tripe slices natural dog treat, food photography, white background, product photo"),
    186: ("Смесь", "dried beef mix udder liver lung tripe natural dog treat assortment, food photography, white background, product photo"),
    187: ("Трахея", "dried beef trachea natural dog treat, food photography, white background, product photo"),
    188: ("Трахея сушёная", "dried beef trachea dehydrated natural dog treat, food photography, white background, product photo"),
    189: ("Трахея кольца", "dried beef trachea rings natural dog treat, food photography, white background, product photo"),
    190: ("Трахея трубки 15см", "dried beef trachea tubes 15cm natural dog treat, food photography, white background, product photo"),
    191: ("Уши опалённые", "scorched beef ears natural dog treat, food photography, white background, product photo"),
    192: ("Уши сушёные опалённые", "dried scorched beef ears dehydrated natural dog treat, food photography, white background, product photo"),
    193: ("Фарш", "dried beef mince minced meat natural dog treat, food photography, white background, product photo"),
    197: ("Палочка яблоня", "apple wood chew stick dog toy natural wooden, white background, product photo"),
    198: ("Палочка груша", "pear wood chew stick dog toy natural wooden, white background, product photo"),
    199: ("Палочка берёза", "birch wood chew stick dog toy natural wooden, white background, product photo"),
    200: ("Палочка вяз", "elm wood chew stick dog toy natural wooden, white background, product photo"),
    201: ("Палочка ольха", "alder wood chew stick dog toy natural wooden, white background, product photo"),
}

# Дубликаты — те же изображения что и у оригиналов
DUPLICATES = {
    194: 189,  # Трахея кольца = 189
    195: 190,  # Трахея трубки = 190
    196: 188,  # Трахея сушёная = 188
}

BANNER_PROMPTS = {
    "banner_01": "natural beef dog treats assortment banner, rustic wooden background, warm tones, horizontal banner",
    "banner_02": "healthy natural dog snacks beef products, modern clean background, horizontal banner",
    "banner_03": "pepito pet brand dried beef treats banner, natural dog food, horizontal product banner",
    "banner_04": "beef dog treats variety flat lay, wooden board background, overhead view banner",
    "banner_05": "happy dog with natural beef treat, lifestyle photo, warm background, horizontal banner",
}


def download_image(prompt, filename, width=800, height=800, retries=3):
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={abs(hash(prompt)) % 999999}"
    for attempt in range(retries):
        try:
            print(f"  Скачиваю: {filename}...", end="", flush=True)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            path = os.path.join(OUTPUT_DIR, filename)
            with open(path, "wb") as f:
                f.write(data)
            print(f" OK ({len(data)//1024}KB)")
            return path
        except Exception as e:
            print(f" RETRY {attempt+1}: {e}")
            time.sleep(5)
    print(f" FAIL")
    return None


def get_db_port():
    import subprocess
    result = subprocess.run(
        ["podman", "port", "odoo_pepito_db", "5432"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        port_str = result.stdout.strip()
        if ":" in port_str:
            return int(port_str.split(":")[-1])
    return 5432


def upload_to_odoo(product_id, image_path):
    try:
        port = get_db_port()
        conn = psycopg2.connect(
            host="localhost", port=port,
            dbname=DB_NAME, user=DB_USER, password=DB_PASS
        )
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()

        cur = conn.cursor()

        # Обновляем image_1920 в product_template
        cur.execute(
            "UPDATE product_template SET image_1920 = %s WHERE id = %s",
            (img_data, product_id)
        )

        # Вычисляем store_fname (sha1 hex)
        with open(image_path, "rb") as f:
            raw = f.read()
        sha1 = hashlib.sha1(raw).hexdigest()
        store_fname = sha1[:2] + "/" + sha1

        # Определяем mimetype
        ext = os.path.splitext(image_path)[1].lower()
        mime = {"jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                ".webp": "image/webp"}.get(ext, "image/jpeg")

        # Обновляем ir_attachment
        cur.execute("""
            UPDATE ir_attachment
            SET store_fname = %s, file_size = %s, checksum = %s, mimetype = %s
            WHERE res_model = 'product.template' AND res_id = %s AND name = 'image_1920'
        """, (store_fname, len(raw), sha1, mime, product_id))

        # Если attachment не было — создаём
        cur.execute("SELECT id FROM ir_attachment WHERE res_model='product.template' AND res_id=%s AND name='image_1920'", (product_id,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO ir_attachment (name, res_model, res_id, store_fname, file_size, checksum, mimetype, type)
                VALUES ('image_1920', 'product.template', %s, %s, %s, %s, %s, 'binary')
            """, (product_id, store_fname, len(raw), sha1, mime))

        # Кладём файл в filestore
        filestore_base = "/var/lib/containers/storage/volumes/pepito_odoo_odoo_pepito_web_data/_data/.local/share/Odoo/filestore/odoo_user_pepito"
        dest_dir = os.path.join(filestore_base, sha1[:2])
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, sha1)
        with open(dest_path, "wb") as f:
            f.write(raw)

        conn.commit()
        conn.close()
        print(f"    → Загружено в Odoo (product_id={product_id})")
        return True
    except Exception as e:
        print(f"    → ОШИБКА загрузки: {e}")
        return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\n=== Генерация {len(PRODUCTS)} изображений товаров ===\n")
    generated = {}

    for product_id, (name, prompt) in PRODUCTS.items():
        filename = f"product_{product_id}.jpg"
        path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(path):
            print(f"  {name} — уже есть, пропускаю")
            generated[product_id] = path
            continue
        path = download_image(prompt, filename)
        if path:
            generated[product_id] = path
        time.sleep(1)

    print(f"\n=== Обработка дубликатов ===\n")
    for dup_id, orig_id in DUPLICATES.items():
        if orig_id in generated:
            import shutil
            src = generated[orig_id]
            dst = os.path.join(OUTPUT_DIR, f"product_{dup_id}.jpg")
            shutil.copy2(src, dst)
            generated[dup_id] = dst
            print(f"  product_{dup_id} ← копия от product_{orig_id}")

    print(f"\n=== Генерация баннеров ===\n")
    for banner_name, prompt in BANNER_PROMPTS.items():
        filename = f"{banner_name}.webp"
        path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(path):
            print(f"  {banner_name} — уже есть")
            continue
        download_image(prompt, filename, width=1200, height=400)
        time.sleep(1)

    print(f"\n=== Загрузка в Odoo ===\n")
    ok = 0
    fail = 0
    for product_id, img_path in generated.items():
        success = upload_to_odoo(product_id, img_path)
        if success:
            ok += 1
        else:
            fail += 1

    print(f"\n=== ГОТОВО: {ok} загружено, {fail} ошибок ===\n")


if __name__ == "__main__":
    main()
