# Virtual-GPTeacher-Language-AI-Tutor (The English version is below this one)
GPTeacher — это исследовательский прототип голосового AI-преподавателя для изучения иностранных языков.
Ассистент работает без клавиатуры, взаимодействуя только голосом через микрофон и динамик, а диалог ведёт с облачным LLM.


**GPTeacher — Виртуальный голосовой преподаватель иностранных языков** 


⚠ Проект опубликован в 2023–2024 гг. и отражает ранний этап развития голосовых LLM-ассистентов.
Некоторые компоненты и API-интеграции могли измениться или стать неактуальными. Репозиторий сохранён как часть портфолио, экспериментальной R&D работы и истории прототипирования, не как production-готовый продукт.

⸻

🌟 **Что это такое**


*GPTeacher — это экспериментальный прототип голосового AI-тьютора, который:*

 • ведёт живой голосовой урок без интерфейса ввода/вывода клавиатурой
 
 • позволяет учить язык через тематические диалоги и вопросы по тексту
 
 • сочетает локальное распознавание речи + облачный LLM + синтез голоса
 


⸻

🔥 **Особенности, которые отличали проект на момент разработки**

**Возможность**          /          **Статус**

Разговорная практика голосом       ✅ реализована, без ограничений

12+ иностранных языков             ✅ через конфигурацию ролей

Кастомные TTS-голоса               ✅ 10+ мужских/женских

Анализ прогресса                   ✅ через сохранение уроков

Локальная автономность             ⚠ частичная, работает на ноутбуке

Реалистичность голоса              ⚠ ограниченная, synthetic звучание

Педагогическая оценка              присутствует



⸻

🧠 **Техническая архитектура**


<img width="1206" height="436" alt="image" src="https://github.com/user-attachments/assets/5b46a163-340b-47b4-a9f1-532bd079bd85" />




Пайплайн обработки:

 1. **Audio Input (microphone stream)**

 • Захват аудио через sounddevice.RawInputStream

 • 16-битный поток int16, 1 канал, 8000 blocksize буфер
 
 2. **Speech-to-Text (локально)**

 • Распознавание на русском/английском с помощью Vosk
 
 • Используются предварительно скачанные акустические модели (локальные директории)
 
 3. **LLM-логика (облако)**
    
 • Ответы генерируются моделью GigaChat
 
 • payload хранит диалог как messages.append(role=USER/ASSISTANT)
 
 4. **Text-to-Speech**
    
 • Ответ LLM переводится в аудио через Yandex SpeechKit
 
 • Формат вывода lpcm → проигрывание через PyAudio stream
 
 5. **Сессионная логика**
    
 • Активация урока — по ключевым фразам (start_chat_msgs)
 
 • Если partial result длится 30+ сек без команды активации, чат сбрасывается
 
 • Если в чате, но 30 сек нет речи → объявляется Новый чат/New chat

⸻

⚙️ **Ключевые технические решения**

1.🎤 **Дискретный голосовой старт уроков**

Ассистент начинает сессию только если пользователь произнёс одну из фраз:

start_chat_msgs = ["давай поговорим", "let's talk", "hablamos?", "parliamo?"]

Это эмуляция wake-up intent без NLU-классификатора.

2. 🧩 **Мультиязыковой intent-triggering через any(start in data)**

Фразы старта детектятся наивным sub-string matching, что:

 • работает быстро
 
 • не требует дополнительной модели классификации
 
 • но даёт False Positives (поэтому антипаттерн для продакшна)

3. 🧠 **Long-Memory payload**

Диалог хранится в структуре:

payload.messages.append(Messages(role=USER, content=data))

payload.messages.append(message_from_assistant)

Это компактный in-context memory для LLM без базы данных.

4. ⏳ **Таймер сброса чатов**

if end - start > 30:

    chat = False

Нужно для:

 • ограничения длины аудио-буфера
 
 • выделения уроков по 30 сек-интервалам (для debug и анализа)


⚙️ **Конфигурация уроков (config.json)**

Ассистент можно гибко настраивать с помощью JSON-файла конфигурации. Все параметры загружаются при старте скрипта и определяют поведение модели, язык урока, тип урока, голос и формат взаимодействия.

📌 *Основные поля конфига*

<img width="1629" height="292" alt="image" src="https://github.com/user-attachments/assets/0c256028-ea63-4876-80aa-97f643f7128d" />



config.json управляет поведением ассистента, форматом уроков и настройками голосовой сессии. При запуске программы параметры автоматически загружаются и определяют, как бот будет вести урок.

**Поле** / **Что делает**

• bot_type — тип языковой модели, которую использует ассистент
(в legacy-версии ориентировались на ChatGPT 4.0 и GigaChat-Pro, сейчас может быть заменён на другой LLM-провайдер)

 • role_or_task — задаёт роль ассистента в уроке
(например: English teacher. Поддерживается 12+ языковых ролей — задаётся промптом)

 • lesson_type — формат практики
 
Доступные режимы:

 • dialogue_on_topic — живой диалог по указанной теме
 
 • questions_on_text — последовательные вопросы по учебному тексту
 
 • topic_of_dialogue — тема диалога для урока в режиме dialogue_on_topic
(задаётся пользователем перед стартом урока)

 • text_for_questions — текст, по которому бот будет составлять и задавать вопросы
(используется только в режиме questions_on_text)

 • save_lesson_to_file — сохранение урока в файл (true / false)
(если true — после урока будет создан лог для анализа ошибок и прогресса речи ученика

⸻


🗂 **Какие зависимости нужны для запуска**

requirements.txt

torch>=2.1.0

numpy>=1.22.0

pandas>=2.0.0

transformers>=4.36.0

accelerate>=0.25.0

bitsandbytes>=0.41.0

vosk>=0.3.45

sounddevice>=0.4.6

pyaudio>=0.2.13

requests>=2.31.0


⸻

💾 **Как запускать локально**

1. Клонировать репозиторий
   
2. Установить зависимости
  
3. Создать API-ключи
  
4. Запустить python файл
   
5. Сказать фразу активации в микрофон
   
6. Начать урок голосом
   
7. Для завершения Ctrl+C


⸻

🔮 **Как можно обновить проект**

Если вы хотите обновить этот старый прототип → вот куда смотреть:

 • Замена string matching на 🧩 NLU intent classifier (BERT/ChatGPT intent)
 
 • Подключение базы памяти (SQLite / VectorDB)
 
 • Обучение моделей эмбеддингов через timm (как планировалось для Wildlife задач)
 
 • Улучшение голоса через современные TTS models

⸻

🧪 **Историческая ценность прототипа**

Несмотря на устаревание, этот проект показал важное:

✨ возможность “говорить” с LLM без печати

✨ держать конфигурацию уроков в JSON как контекстную память

✨ создать первый open-source voice-тьютора на базе GPT среди школьных инженерных проектов

*Проект представлялся на инженерных и AI-форумах, а разработка велась при поддержке лингвистов.
Это был старт эксперимента, который сегодня можно переосмыслить на новых технологиях 🔄.*

⸻

🏷 **Авторство**

Дмитриева Евгения Дмитриевна, Москва, 2023 -2024 гг.

https://t.me/angel_eugeniya

eugeniya.dm@gmail.com

> Этот репозиторий размещен в нейтральной организации на GitHub для сохранения портфолио и отслеживания вкладов. Он не отражает принадлежность к работодателю.


**ENGLISH**

**Virtual-GPTeacher-Language-AI-Tutor** 

*GPTeacher — Voice-First LLM Language Tutor (Legacy Prototype)*

⚠️ Originally prototyped and demonstrated in 2023–2024.
This repository is preserved as part of a research, hardware-integrated AI prototype portfolio, not as a production-ready system. Some APIs, model endpoints, and voices may have changed since the original development phase.

⸻

🌟 **What is GPTeacher?**

GPTeacher is an experimental voice-only AI language tutor that:

 • interacts without a keyboard, using microphone capture and speaker output
 
 • enables unlimited spoken conversation practice
 
 • supports 12+ languages via configurable system roles
 
 • combines:
 
 1. Local offline speech recognition
 
 2. Cloud-hosted LLM responses
 
 3. Text-to-speech voice synthesis
 
 4. Session segmentation via silence timers
 
 • uses a 3D-printed robotic head based on open-source designs as its audio output hardware

⸻

🔥 **Key Capabilities at the Time of Development**

**Feature** / **Status**

Voice conversation practice ✅ implemented, no limits

12+ foreign languages ✅ via role configuration

Custom TTS voices ✅ 10+ male/female

Lesson history for progress analysis ✅ supported

Local autonomy ⚠ partial, ran on laptop

Voice realism ⚠ synthetic sounding

Pedagogical evaluation experience builts-in


⸻

🧠 **Technical Architecture**


<img width="1206" height="436" alt="image" src="https://github.com/user-attachments/assets/9287f923-2a4f-4b15-ae5d-0f571e9fb578" />


*Processing pipeline*

 1.  **Audio Input (Microphone Stream Capture)**
 
 • Audio is captured using sounddevice.RawInputStream
 
 • Format: 16-bit int16, 1 channel, 8000 frame buffer
 
 2.  **Speech-to-Text (Offline, Local)**
 
 • Speech is recognized using local acoustic models from Vosk Community
 
 • No internet connection is needed for recognition
 
 • English and Russian language models are supported
 
 3.  **LLM Response Generation (Cloud)**
 
 • Responses were generated using an early version of GigaChat
 
 • Dialogue was stored in a payload.messages.append(role=USER/ASSISTANT) chain

 4.  **Text-to-Speech (TTS Voice Synthesis)**

 • LLM reply text is converted to audio using Yandex SpeechKit
 
 • Output format: lpcm played via PyAudio stream
 
 5.  **Session Control & Auto-Reset**
 
 • The assistant “wakes up” using naïve substring intent detection (any(start in data))
 
 • If partial speech input exceeds 30 sec without activation intent, chat resets
 
 • If silence lasts 30 sec during session, assistant announces:
“New chat started” / “Новый чат”

⸻

⚙️ **Core Technical Design Choices**

1. 🎤**Wake-Up Intent Imitation (No NLU Model)**

start_chat_msgs = ["давай поговорим", "let's talk", "hablamos?", "parliamo?"]

A fast, model-free wake-word intent simulation.

2. 🧩 **Multilingual Triggering via Sub-String Matching**

if any(msg in data for msg in start_chat_msgs)

✅ Fast, no extra ML model required

⚠ Not reliable for production (false positives)

3. 🧠 **In-Context Dialogue Memory**

payload.messages.append(Messages(role=USER, content=data))

payload.messages.append(message_from_assistant)

A lightweight chat memory stored directly in the prompt.

4. ⏳ **Chat Reset Timer**

if end - start > 30:

    chat = False

Ensures conversation is segmented into short lesson sessions.

⸻


⚙️ **Lesson configuration (config.json)**

The assistant can be flexibly configured via a JSON configuration file.

All parameters are loaded at startup and define:
 
 • which LLM is used
 
 • what teacher role the assistant plays
 
 • which lesson format is active
 
 • which language and voice are used
 
 • how long to wait before auto-resetting the chat

📌 **Main config fields**

<img width="1629" height="292" alt="image" src="https://github.com/user-attachments/assets/b885d532-849f-4030-b7c1-a1ccf5423b0c" />


 • bot_type — specifies the language model or LLM provider used by the assistant
(legacy version focused on ChatGPT 4.0 or GigaChat-Pro, can now be replaced with other cloud-based LLMs)

 • role_or_task — defines the assistant’s role during the lesson
(e.g., English teacher. The system supports 12+ language teaching roles provided via prompt instructions)

 • lesson_type — determines the format of the language practice
 
Currently supported modes:

 • dialogue_on_topic — natural conversation based on a given topic
 
 • questions_on_text — sequential questions generated from a learning text
 
 • topic_of_dialogue — the topic used when the lesson is in dialogue_on_topic mode
(provided by the user before or during session activation)

 • text_for_questions — the study text used to generate questions in questions_on_text mode
(ignored if the lesson is not text-based)

 • save_lesson_to_file — enables or disables lesson logging to a file
(if true → a lesson log is created for later error analysis and progress review)

⸻


🗂 **Required Dependencies**

requirements.txt

torch>=2.0.0

numpy>=1.22.0

pandas>=2.0.0

transformers>=4.36.0

accelerate>=0.25.0

bitsandbytes>=0.41.0

vosk>=0.3.45

sounddevice>=0.4.6

pyaudio>=0.2.13

requests>=2.31.0


⸻

🚀 **Installing and Running Locally**

1. Clone the repository from GitHub

2. Install dependencies

3. Create your API keys

4. Run the Python script

5. Activate with your voice using one of the intent phrases

6. Start your lesson by speaking

7. Stop the program using Ctrl+C


⸻

🔮 **Modern Update Path for the Prototype**

If you want to revive and modernize this legacy prototype, consider:

 • replacing string matching with an intent classifier (BERT or OpenAI intent models)
 
 • storing persistent memory in SQLite or a vector database
 
 • improving voice realism with modern TTS models
 
 • moving logic from laptop to a Raspberry Pi device for full autonomy

⸻

🧪 **Historical Value**

Even though the prototype may now be outdated, it demonstrated:

✨ that you can speak with an LLM without typing

✨ that JSON configs can act as early “lesson memory”

✨ one of the first open voice-based LLM tutoring prototypes built at school level


Development was assisted by university linguists at an early stage, and the project was presented at engineering and AI forums.

⸻

🏷️ **Author**

Evgeniya Dmitrieva 
📍 Moscow, Russia, 2023-2024

Acoustic models sourced from Vosk Community, TTS powered by Yandex SpeechKit, and LLM connected to GigaChat.

Me on Telegram: https://t.me/angel_eugeniya

eugeniya.dm@gmail.com

> This repository is hosted under a neutral GitHub organization for portfolio preservation and contribution tracking. It does not reflect employer affiliation.




