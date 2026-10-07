# Установка

Нужны: Git, Python, `ffmpeg`, `yt-dlp`, Wireshark (`tshark`, только для курсов с трафиком, профиль `network`), Obsidian (для чтения заметок) и движок распознавания речи. Движок выбирается автоматически по железу.

Команды ниже можно выполнить самому или попросить Claude Code. Сообщение для Claude: «Прочитай SETUP.md и подготовь окружение: установи недостающее ПО и Python-пакеты, потом запусти scripts/doctor.py и покажи результат». Он спросит разрешение перед каждой установкой. Шаг 0 (сертификаты) Claude выполнить не может.

## Шаг 0. Сертификаты Минцифры (обязательно, делает пользователь)

Сайт платформы обучения (`lms.edu.ptsecurity.com`) не откроется без российских корневых сертификатов Минцифры. Без этого шага не заработает ни LMS, ни работа ассистента с ней.

1. Скачайте сертификаты на странице: https://www.gosuslugi.ru/landing/crt
2. Установите их **сами**, следуя инструкции на этой странице, для вашей ОС (Windows или macOS). Ассистент не устанавливает сертификаты: это изменение настроек безопасности.
3. Перезапустите браузер и приложение Claude.
4. Откройте адрес LMS из `course.md` во встроенном браузере приложения Claude (и, если используете, в Google Chrome). Страница должна открыться без предупреждения о сертификате. Затем войдите в свой аккаунт.

Если появляется предупреждение о сертификате, сертификаты установлены не полностью. Повторите шаг 2.

## Windows (PowerShell)

```powershell
winget install Git.Git
winget install Python.Python.3.12
winget install Gyan.FFmpeg
winget install yt-dlp.yt-dlp
winget install WiresharkFoundation.Wireshark   # только для профиля network
winget install Obsidian.Obsidian
```

`winget` пропускает программы, которые уже установлены, и ничего не перезаписывает. Obsidian нужен, чтобы читать заметки. Если он уже есть, пропустите эту строку.

Закройте и откройте PowerShell, чтобы обновился `PATH`. Затем в папке проекта:

```powershell
pip install -r scripts/requirements.txt
```

Если есть видеокарта NVIDIA (нужен свежий драйвер):

```powershell
pip install -r scripts/requirements-cuda.txt
```

`transcribe.py` выберет `faster-whisper`, модель `large-v3`, режим CUDA `float16`. Первый запуск скачает модель (около 3 ГБ). Если GPU не заработает, скрипт сам перейдёт на CPU с моделью `medium`.

Без видеокарты NVIDIA скрипт возьмёт модель `medium` на CPU. Это медленнее. Чтобы ускорить, задайте `WHISPER_MODEL=small`.

## macOS (Terminal)

```bash
brew install git python ffmpeg yt-dlp whisper-cpp
brew install --cask obsidian
brew install --cask wireshark   # только для профиля network
mkdir -p ~/.cache/whisper-cpp
```

Скачайте файл модели `ggml-large-v3.bin` (около 3 ГБ) с `huggingface.co/ggerganov/whisper.cpp` в `~/.cache/whisper-cpp/`. На Mac скрипт использует `whisper.cpp` с Metal.

## Obsidian

Заметки читаются в Obsidian. Шаблон ничего не настраивает в самой программе. Откройте папку проекта через **Open folder as vault**: Obsidian создаст папку `.obsidian` только внутри проекта. Ваши другие vault'ы не затрагиваются.

## Проверка

```bash
python scripts/doctor.py
```

На macOS команда `python3`, если `python` не найден. Скрипт покажет, чего не хватает и чем это исправить.

## Ручной выбор движка

| Переменная | Значения | Зачем |
|---|---|---|
| `WHISPER_BACKEND` | `whispercpp`, `faster-whisper` | принудительно выбрать движок |
| `WHISPER_MODEL` | `large-v3`, `medium`, `small` | принудительно выбрать модель |

Проверить выбор без запуска: `python scripts/transcribe.py media/w1/файл.mp4 --dry-run`.

## Типичные проблемы

- **`python` не найден на Windows**: переустановите Python и отметьте «Add python.exe to PATH», либо используйте `py`.
- **`faster-whisper` не ставится**: вероятно, слишком новый Python. Ставьте 3.12.
- **`Could not load library cudnn...`**: выполните `pip install -r scripts/requirements-cuda.txt`.
- **Кракозябры в CSV или заметках**: файлы должны быть в UTF-8 с LF. Это задаёт `.gitattributes`.
