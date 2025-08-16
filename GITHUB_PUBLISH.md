# Инструкции по публикации в GitHub

## 🚀 Публикация проекта Bitcoin Legacy Wallet Scanner

### Шаг 1: Создание репозитория на GitHub

1. Перейдите на [GitHub.com](https://github.com) и войдите в свой аккаунт
2. Нажмите кнопку **"New repository"** (зеленый "+" в правом верхнем углу)
3. Заполните форму:
   - **Repository name**: `bitcoin-legacy-scanner` (или другое название)
   - **Description**: `High-performance Bitcoin legacy wallet scanner with TUI interface`
   - **Visibility**: Выберите Public или Private
   - **Initialize this repository with**: НЕ ставьте галочки (у нас уже есть файлы)
4. Нажмите **"Create repository"**

### Шаг 2: Подключение локального репозитория к GitHub

После создания репозитория GitHub покажет инструкции. Выполните следующие команды:

```bash
# Добавить удаленный репозиторий (замените YOUR_USERNAME на ваше имя пользователя)
git remote add origin https://github.com/YOUR_USERNAME/bitcoin-legacy-scanner.git

# Переименовать основную ветку в main (современный стандарт)
git branch -M main

# Отправить код в GitHub
git push -u origin main

# Отправить тег
git push origin v1.0.0
```

### Шаг 3: Настройка репозитория

#### 3.1 Описание репозитория
В настройках репозитория добавьте:
- **Website**: Оставьте пустым
- **Topics**: `bitcoin`, `wallet`, `scanner`, `cryptography`, `python`, `tui`, `legacy`, `p2pkh`

#### 3.2 Настройка веток
1. Перейдите в **Settings** → **Branches**
2. Добавьте правило для ветки `main`:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging

#### 3.3 Настройка Issues и Projects
1. Включите **Issues** (должно быть включено по умолчанию)
2. Включите **Projects** если планируете использовать
3. Включите **Wiki** для дополнительной документации

### Шаг 4: Настройка GitHub Pages (опционально)

Если хотите создать веб-страницу проекта:

1. Перейдите в **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: main
4. **Folder**: /docs
5. Нажмите **Save**

### Шаг 5: Создание первого релиза

1. Перейдите в **Releases**
2. Нажмите **"Create a new release"**
3. **Tag version**: `v1.0.0`
4. **Release title**: `Initial Release - Bitcoin Legacy Wallet Scanner`
5. **Description**:
```markdown
## 🎉 Initial Release

### Features
- High-performance Bitcoin legacy P2PKH address generation
- TUI interface with real-time statistics
- Batch balance checking via bitcoin-cli
- Multiprocessing architecture
- State persistence and resume functionality
- File rotation and logging

### Performance
- Generation: ~100,000 addresses/min
- Checking: ~50,000 addresses/min
- Automatic CPU core detection

### Requirements
- Python 3.10+
- Ubuntu/Debian Linux
- Bitcoin Core full node
- 4GB+ RAM

### Security Warning
⚠️ **This tool generates private keys! Use ONLY for educational purposes.**

### Installation
```bash
git clone https://github.com/YOUR_USERNAME/bitcoin-legacy-scanner.git
cd bitcoin-legacy-scanner
pip install -r requirements.txt
python3 btc_legacy_scanner.py
```

### Documentation
- [README](README.md) - English documentation
- [README_RU](README_RU.md) - Russian documentation
- [Examples](EXAMPLES.md) - Usage examples
- [Project Summary](PROJECT_SUMMARY.md) - Project overview
```

6. Нажмите **"Publish release"**

### Шаг 6: Настройка CI/CD

GitHub Actions уже настроены в файле `.github/workflows/ci.yml`. Они будут автоматически запускаться при:
- Push в ветки `main` и `develop`
- Pull Request в ветку `main`

### Шаг 7: Создание Wiki (опционально)

1. Перейдите в **Wiki**
2. Создайте главную страницу с описанием проекта
3. Добавьте страницы:
   - Installation Guide
   - Configuration
   - Troubleshooting
   - Performance Tuning

### Шаг 8: Настройка Community Health

GitHub автоматически проверит здоровье проекта. Убедитесь что у вас есть:
- ✅ README.md
- ✅ LICENSE
- ✅ .gitignore
- ✅ Issue templates
- ✅ Pull request template
- ✅ Code of Conduct (опционально)

### Шаг 9: Продвижение проекта

#### 9.1 Социальные сети
- Поделитесь в Twitter/X
- Опубликуйте в Reddit (r/bitcoin, r/cryptography)
- Добавьте в LinkedIn

#### 9.2 Технические платформы
- [PyPI](https://pypi.org/) - если планируете публиковать как пакет
- [Docker Hub](https://hub.docker.com/) - если создадите Docker образ
- [Bitcoin Stack Exchange](https://bitcoin.stackexchange.com/)

### Шаг 10: Мониторинг и поддержка

#### 10.1 Регулярные задачи
- Отвечайте на Issues
- Рассматривайте Pull Requests
- Обновляйте зависимости
- Мониторьте безопасность

#### 10.2 Метрики
- Stars и Forks
- Issues и Pull Requests
- Downloads (если на PyPI)
- Community engagement

## 🔗 Полезные ссылки

- [GitHub Guides](https://guides.github.com/)
- [GitHub Community](https://github.com/community)
- [GitHub Security](https://github.com/security)
- [GitHub Actions](https://github.com/features/actions)

## 📝 Чек-лист публикации

- [ ] Создан репозиторий на GitHub
- [ ] Код загружен в репозиторий
- [ ] Настроены ветки и правила
- [ ] Создан первый релиз
- [ ] Настроены GitHub Actions
- [ ] Добавлены теги для поиска
- [ ] Создана Wiki (опционально)
- [ ] Проект продвигается в сообществе

---

**Удачи с публикацией! 🚀**

Ваш проект Bitcoin Legacy Wallet Scanner готов к публикации и имеет все необходимые файлы для успешного запуска на GitHub.
