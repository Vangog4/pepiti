# Подключение эквайринга Т-Банка (Tinkoff) — pepitopet.ru

## Что сделано на сайте

1. Модуль Odoo **`payment_tinkoff`** (`addons/payment_tinkoff/`)
2. Провайдер «Т-Банк (Tinkoff)» в payment providers
3. Callback-роуты:
   - **Success/Fail return:** `https://pepitopet.ru/payment/tinkoff/return`
   - **Notification (webhook):** `https://pepitopet.ru/payment/tinkoff/notification`
4. Валюта компании: **RUB**
5. eCommerce + website_payment уже установлены

## Что нужно от вас (ЛК Т-Банка)

В [личном кабинете](https://business.tbank.ru/oplata/main) / интернет-эквайринг:

| Параметр | Где взять |
|---|---|
| **TerminalKey** | Настройки терминала |
| **Password** | Настройки терминала (для Token) |
| **Тестовый терминал** | Отдельный DEMO TerminalKey для песочницы |

В настройках терминала укажите:

```
Notification URL: https://pepitopet.ru/payment/tinkoff/notification
Success URL:      https://pepitopet.ru/payment/tinkoff/return
Fail URL:         https://pepitopet.ru/payment/tinkoff/return
```

(Success/Fail также передаются в каждом Init — дублирование в ЛК полезно.)

Онлайн-касса (54-ФЗ): если касса подключена к эквайрингу — оставьте «Передавать чек (Receipt)» = Да и выберите СНО (УСН/ОСН).

## Настройка в Odoo (после установки модуля)

1. Войти в бэкенд: `https://pepitopet.ru/web` (или :8071)
2. **Website → Configuration → Payment Providers**  
   (или **Invoicing → Configuration → Payment Providers**)
3. Открыть **Т-Банк (Tinkoff)**
4. Вкладка Credentials:
   - TerminalKey = …
   - Password = …
   - Taxation = ваша СНО
   - Send receipt = Да (если касса)
5. **State** → `Test` (сначала) или `Enabled` (прод)
6. **Publish** на сайте (is_published)
7. Сохранить

## Установка модуля (уже можно выполнить)

```bash
cd /root/pepito/odoo
# модуль в addons/ — volume смонтирован
podman exec odoo_pepito_app odoo -d odoo_user_pepito \
  -i payment_tinkoff \
  --stop-after-init \
  --http-port=8099 --gevent-port=8098

podman restart odoo_pepito_app
```

Или из UI: Apps → Update Apps List → найти «T-Bank» → Install.

## Проверка

1. Test TerminalKey + State=Test
2. `/shop` → товар в корзину → Checkout → **Т-Банк**
3. Оплата тестовой картой из документации Т-Банка
4. Возврат на `/payment/status` → заказ Paid
5. В логах Odoo: `Tinkoff notification` / `Tinkoff return`

```bash
podman logs -f odoo_pepito_app | grep -i tinkoff
```

## Поток платежа

```
Checkout Odoo
  → payment.transaction
  → Init API (securepay.tinkoff.ru/v2/Init)
  → redirect PaymentURL
  → клиент платит на стороне Т-Банка
  → NotificationURL (server) → _process → done
  → ReturnURL (browser) → GetState → /payment/status
```

## Безопасность

- Password хранится в `payment.provider` (группы system)
- Token (SHA-256) проверяется на webhook (в test mode допускает отсутствие Token)
- HTTPS обязателен для NotificationURL (pepitopet.ru уже на HTTPS)

## Не путать

| Платёж | Где |
|---|---|
| **Т-Банк эквайринг** | Сайт pepitopet.ru (этот модуль) |
| **Telegram Stars** | Бот @pepitopetbot (premium 299 ⭐) |

Это разные каналы монетизации.
