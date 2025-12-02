
📌 **Инструкции для README — установка моделей речи оффлайн**

⸻

🗣️ **Download and Install Speech Recognition Models**


❗ Акустические модели не хранятся в репозитории напрямую из-за размера. Они должны быть загружены отдельно перед первым запуском.

Используются модели от Vosk Community:

 1. Создайте папку для моделей:

!mkdir -p models/vosk-en

!mkdir -p models/vosk-ru


 2. Скачайте и распакуйте модели:

**🇬🇧 Английская модель**

!wget https://alphacephei.com/vosk/models/vosk-model-en-0.22.zip -O models/vosk-en/model.zip

!unzip models/vosk-en/model.zip -d models/vosk-en

!rm models/vosk-en/model.zip

**🇷🇺 Русская модель**

!wget https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip -O models/vosk-ru/model.zip

!unzip models/vosk-ru/model.zip -d models/vosk-ru

!rm models/vosk-ru/model.zip

 3. После установки структура будет такой:

models/

│── vosk-en/

│── vosk-ru/




🏷 badges (Build ✅ | License MIT ✅ | Voice-first AI 🎤)

Скажи — какой ОС будем делать скрипт первым? 😎
