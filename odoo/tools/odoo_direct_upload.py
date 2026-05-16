#!/usr/bin/env python3
"""Загружает изображения в Odoo через ORM, минуя HTTP сервер."""
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import odoo
import odoo.api
import odoo.modules.registry
from odoo.tools import config

config.parse_config([
    '--config', '/etc/odoo/odoo.conf',
    '--database', 'odoo_user_pepito',
    '--no-http',
])

registry = odoo.modules.registry.Registry.new('odoo_user_pepito')

import base64, os

LABELED_DIR = '/tmp/labeled_images'

PRODUCTS = {
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

with registry.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    ok = fail = 0
    for pid, name in sorted(PRODUCTS.items()):
        img_path = os.path.join(LABELED_DIR, f'product_{pid}.webp')
        if not os.path.exists(img_path):
            print(f'  [ПРОПУСК] {name}')
            fail += 1
            continue
        try:
            with open(img_path, 'rb') as f:
                img_b64 = base64.b64encode(f.read()).decode()
            pt = env['product.template'].browse(pid)
            if not pt.exists():
                print(f'  [НЕТ В БД] {name} id={pid}')
                fail += 1
                continue
            pt.write({'image_1920': img_b64})
            cr.commit()
            print(f'  [OK] {name}')
            ok += 1
        except Exception as e:
            cr.rollback()
            print(f'  [ERR] {name}: {e}')
            fail += 1
    print(f'\n=== ИТОГО: {ok} OK, {fail} ошибок ===')
