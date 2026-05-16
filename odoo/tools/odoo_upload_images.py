import base64, os, sys

LABELED_DIR = "/tmp/labeled_images"

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

env = self.env  # noqa: F821 — доступно в odoo shell

ok = 0
fail = 0
for pid, name in sorted(PRODUCT_NAMES.items()):
    img_path = os.path.join(LABELED_DIR, f"product_{pid}.webp")
    if not os.path.exists(img_path):
        print(f"  [ПРОПУСК] {name} — файл не найден: {img_path}")
        fail += 1
        continue
    try:
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        product = env["product.template"].browse(pid)
        if not product.exists():
            print(f"  [ПРОПУСК] {name} — товар id={pid} не найден в БД")
            fail += 1
            continue
        product.write({"image_1920": img_b64})
        env.cr.commit()
        print(f"  [OK] {name} (id={pid})")
        ok += 1
    except Exception as e:
        print(f"  [ERR] {name}: {e}")
        env.cr.rollback()
        fail += 1

print(f"\n=== ИТОГО: {ok} OK, {fail} ошибок ===")
