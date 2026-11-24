# === ВАРИАНТ ===
# ДЗ3 · вариант для: TranHuyHiep
# Логи — в папке hw3/logs/ (их создал hw_variant.py). Файл <сервер>.log пишет сервер <сервер>.
# SERVER_TIMEZONES: сервер -> часовой пояс, где он стоит (имя для zoneinfo.ZoneInfo).
# Время в строке без пояса (без Z и без +03:00) — местное время сервера в этом поясе.
SERVER_TIMEZONES = {
    "cache": "Asia/Yekaterinburg",
    "orders": "Europe/Athens",
    "payments": "UTC",
    "storage": "Europe/Warsaw",
}
# === КОНЕЦ ВАРИАНТА ===