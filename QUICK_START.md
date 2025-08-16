# 🚀 Быстрый старт - Bitcoin Legacy Wallet Scanner

## ⚡ Установка и запуск за 5 минут

### 1. Проверка системы
```bash
python3 check_system.py
```

### 2. Автоматическая установка (Ubuntu/Debian)
```bash
chmod +x install.sh
./install.sh
```

### 3. Запуск сканера
```bash
# TUI режим (рекомендуется)
python3 btc_legacy_scanner.py

# Headless режим
python3 btc_legacy_scanner.py --headless --start
```

## 🎯 Управление TUI
- **s** - Запуск/Возобновление
- **p** - Пауза  
- **q** - Выход

## 📊 Тестирование производительности
```bash
python3 test_performance.py
```

## 🔧 Основные настройки
Отредактируйте `config.yaml`:
```yaml
batch_size: 512          # Размер пакета для RPC
gen_workers: auto        # Автоопределение CPU ядер
rpc_workers: auto        # Автоопределение RPC воркеров
```

## 📁 Выходные файлы
- `out/btc_adress_w_balance.csv` - Адреса с балансом
- `out/bad_adress` - Адреса без баланса
- `scanner.log` - Лог работы
- `state.json` - Состояние для возобновления

## ⚠️ ВАЖНО
**ТОЛЬКО для образовательных целей!**
**НЕ используйте для реальных кошельков!**

---

**Подробная документация**: [README.md](README.md) | [README_RU.md](README_RU.md)
**Примеры использования**: [EXAMPLES.md](EXAMPLES.md)
**Публикация в GitHub**: [GITHUB_PUBLISH.md](GITHUB_PUBLISH.md)
