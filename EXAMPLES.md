# Примеры использования Bitcoin Legacy Wallet Scanner

## 🚀 Быстрый старт

### 1. Первый запуск
```bash
# Проверка системы
python3 check_system.py

# Запуск с TUI интерфейсом
python3 btc_legacy_scanner.py

# Или в headless режиме
python3 btc_legacy_scanner.py --headless --start
```

### 2. Тестирование производительности
```bash
# Тест генерации ключей
python3 test_performance.py

# Тест в dry-run режиме (5 минут)
python3 btc_legacy_scanner.py --headless --start --duration 300 --dry-run
```

## 🎯 Режимы работы

### TUI режим (интерактивный)
```bash
python3 btc_legacy_scanner.py
```
**Управление:**
- `s` - Запуск/Возобновление
- `p` - Пауза
- `q` - Выход

### Headless режим (фоновый)
```bash
# Запуск на 1 час
python3 btc_legacy_scanner.py --headless --start --duration 3600

# Запуск до прерывания
python3 btc_legacy_scanner.py --headless --start

# С пользовательскими настройками
python3 btc_legacy_scanner.py --headless --start \
    --batch-size 1024 \
    --gen-workers 8 \
    --rpc-workers 4
```

## ⚙️ Настройка производительности

### Оптимизация для мощных систем
```yaml
# config.yaml
batch_size: 1024          # Большие пакеты для RPC
gen_workers: 16           # Много воркеров генерации
rpc_workers: 8            # Много RPC воркеров
queue_max: 500000         # Большая очередь
rpc_timeout_sec: 180      # Увеличенный таймаут
```

### Оптимизация для слабых систем
```yaml
# config.yaml
batch_size: 256           # Малые пакеты
gen_workers: 2            # Меньше воркеров
rpc_workers: 2            # Меньше RPC воркеров
queue_max: 50000          # Малая очередь
rpc_timeout_sec: 60       # Малый таймаут
```

## 🔧 Сценарии использования

### 1. Образовательные цели
```bash
# Генерация 1000 адресов для изучения
python3 btc_legacy_scanner.py --headless --start --duration 60

# Анализ результатов
echo "Найдено адресов с балансом:"
wc -l out/btc_adress_w_balance.csv

echo "Всего проверено адресов:"
wc -l out/bad_adress
```

### 2. Тестирование производительности
```bash
# Бенчмарк генерации
python3 test_performance.py

# Тест RPC производительности
python3 btc_legacy_scanner.py --headless --start --duration 600 \
    --batch-size 512 --rpc-workers 4
```

### 3. Мониторинг в реальном времени
```bash
# Запуск сканера
python3 btc_legacy_scanner.py --headless --start &

# Мониторинг логов
tail -f scanner.log

# Мониторинг результатов
watch -n 5 'echo "Найдено с балансом:"; wc -l out/btc_adress_w_balance.csv; echo "Проверено:"; wc -l out/bad_adress'
```

## 📊 Анализ результатов

### Статистика по найденным адресам
```bash
# Подсчет адресов с балансом
echo "Адреса с положительным балансом:"
wc -l out/btc_adress_w_balance.csv

# Анализ балансов
echo "Топ-10 по балансу:"
sort -t';' -k3 -nr out/btc_adress_w_balance.csv | head -10

# Общая сумма найденных балансов
echo "Общая сумма (сатоши):"
awk -F';' '{sum += $3} END {print sum}' out/btc_adress_w_balance.csv
```

### Анализ производительности
```bash
# Извлечение метрик из логов
grep "Generation rate" scanner.log | tail -20
grep "Check rate" scanner.log | tail -20

# Анализ ошибок
grep "ERROR" scanner.log | wc -l
grep "WARN" scanner.log | wc -l
```

## 🚨 Устранение неполадок

### Проблема: Низкая производительность
```bash
# Проверка использования ресурсов
htop
iostat -x 1
iotop

# Оптимизация конфигурации
python3 btc_legacy_scanner.py --headless --start \
    --batch-size 1024 \
    --gen-workers $(nproc) \
    --rpc-workers 8
```

### Проблема: Ошибки RPC
```bash
# Проверка статуса Bitcoin Core
bitcoin-cli getblockchaininfo

# Проверка RPC конфигурации
cat ~/.bitcoin/bitcoin.conf | grep rpc

# Перезапуск Bitcoin Core
sudo systemctl restart bitcoind
```

### Проблема: Нехватка памяти
```bash
# Мониторинг памяти
free -h
ps aux --sort=-%mem | head -10

# Уменьшение нагрузки
python3 btc_legacy_scanner.py --headless --start \
    --batch-size 256 \
    --gen-workers 2 \
    --rpc-workers 2
```

## 🔒 Безопасность

### Защита выходных файлов
```bash
# Создание защищенной директории
mkdir -p ~/secure-bitcoin-scanner
chmod 700 ~/secure-bitcoin-scanner

# Запуск с защищенной директорией
python3 btc_legacy_scanner.py --output-dir ~/secure-bitcoin-scanner

# Шифрование результатов
gpg -e -r your-email@example.com out/btc_adress_w_balance.csv
```

### Мониторинг безопасности
```bash
# Проверка прав доступа
ls -la out/
ls -la ~/.bitcoin/

# Мониторинг сетевых соединений
netstat -tulpn | grep bitcoind
ss -tulpn | grep bitcoind
```

## 📈 Оптимизация для продакшена

### Автоматический запуск
```bash
# Создание systemd сервиса
sudo tee /etc/systemd/system/bitcoin-scanner.service > /dev/null << EOF
[Unit]
Description=Bitcoin Legacy Scanner
After=bitcoind.service
Requires=bitcoind.service

[Service]
Type=simple
User=bitcoin
WorkingDirectory=/home/bitcoin/bitcoin-scanner
ExecStart=/home/bitcoin/bitcoin-scanner/venv/bin/python3 btc_legacy_scanner.py --headless --start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Включение автозапуска
sudo systemctl enable bitcoin-scanner
sudo systemctl start bitcoin-scanner
```

### Мониторинг и алерты
```bash
# Скрипт мониторинга
cat > monitor_scanner.sh << 'EOF'
#!/bin/bash
SCANNER_PID=$(pgrep -f btc_legacy_scanner.py)

if [ -z "$SCANNER_PID" ]; then
    echo "ALERT: Bitcoin Scanner не запущен!"
    # Отправка уведомления
    # curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    #     -d "chat_id=$CHAT_ID" -d "text=Bitcoin Scanner остановлен!"
fi
EOF

chmod +x monitor_scanner.sh

# Добавление в crontab
echo "*/5 * * * * /home/bitcoin/bitcoin-scanner/monitor_scanner.sh" | crontab -
```

## 🎓 Образовательные примеры

### Изучение Bitcoin адресов
```bash
# Генерация небольшого количества адресов для изучения
python3 btc_legacy_scanner.py --headless --start --duration 300

# Анализ структуры адресов
echo "Примеры сгенерированных адресов:"
head -5 out/bad_adress

echo "Примеры приватных ключей (WIF):"
head -5 out/btc_adress_w_balance.csv | cut -d';' -f2
```

### Понимание Base58Check
```bash
# Проверка контрольных сумм
python3 -c "
from btc_legacy_scanner import Base58Check
import hashlib

# Пример проверки адреса
address = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
print(f'Адрес: {address}')
print(f'Длина: {len(address)} символов')
print(f'Начинается с: {address[0]}')
"
```

## 🔗 Интеграция с другими инструментами

### Экспорт в базу данных
```bash
# SQLite импорт
sqlite3 bitcoin_addresses.db << EOF
CREATE TABLE addresses (
    address TEXT PRIMARY KEY,
    private_key TEXT,
    balance_sats INTEGER,
    found_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

.mode csv
.separator ';'
.import out/btc_adress_w_balance.csv addresses
EOF
```

### Интеграция с Grafana
```bash
# Экспорт метрик в формате Prometheus
python3 -c "
import time
import json

metrics = {
    'bitcoin_scanner_generated_total': 0,
    'bitcoin_scanner_checked_total': 0,
    'bitcoin_scanner_found_with_balance': 0,
    'bitcoin_scanner_generation_rate': 0.0,
    'bitcoin_scanner_check_rate': 0.0
}

# Экспорт метрик
print('# HELP bitcoin_scanner_generated_total Total addresses generated')
print('# TYPE bitcoin_scanner_generated_total counter')
print(f'bitcoin_scanner_generated_total {metrics[\"bitcoin_scanner_generated_total\"]}')

print('# HELP bitcoin_scanner_checked_total Total addresses checked')
print('# TYPE bitcoin_scanner_checked_total counter')
print(f'bitcoin_scanner_checked_total {metrics[\"bitcoin_scanner_checked_total\"]}')
"
```

---

**Примечание**: Все примеры предназначены для образовательных целей. Не используйте для реальных кошельков!
