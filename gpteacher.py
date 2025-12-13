import sounddevice as sd
import vosk, queue, json
import pyaudio
import time
import json
import requests
import argparse
import os.path
from speechkit import Session, SpeechSynthesis
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

# https://github.com/ai-forever/gigachat
# https://github.com/TikhonP/yandex-speechkit-lib-python
# https://habr.com/ru/articles/681566/
# https://github.com/roma1n/yandexgpt-api-python-example/blob/main/query.py
# https://habr.com/ru/articles/780008/

oauth_token = "your_token"
catalog_id = "your_catalod_id"
gigachat_creds = 'your_creds'

'''
# If you want to add config.json
# =================== Load configuration ===================
with open("config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

print("Config loaded:", cfg)

# Забираем параметры
bot_type = cfg.get("bot_type", "chatgpt")
role_or_task = cfg.get("role_or_task", "english_teacher")
lesson_type = cfg.get("lesson_type", "dialogue_on_topic")
topic_of_dialogue = cfg.get("topic_of_dialogue", "")
text_for_questions = cfg.get("text_for_questions", "")
save_lesson = cfg.get("save_lesson_to_file", False)

# Пути из конфига для Vosk моделей
vosk_ru = cfg.get("vosk_model_ru_path", "models/vosk-ru")
vosk_en = cfg.get("vosk_model_en_path", "models/vosk-en")
'''

# ============================= vosk ===============================
q = queue.Queue()

devices = sd.query_devices()
print("Select device id: \n", devices)

dev_id = 0 # default

try:
    dev_id = int(input())
except ValueError:
    print("Using default value: 0")

samplerate = int(sd.query_devices(dev_id, 'input')['default_samplerate'])

# ============================= gigachat ============================
payload = Chat(
    messages=[
        Messages(
            role = MessagesRole.SYSTEM,
            content = "Представь, что ты преподаватель английского языка, а я твой ученик. Давай побеседуем на английском языке о Музее Будущего в Дубае. Ты можешь меня спросить о том, что меня больше всего впечатлило и что я бы порекомендовала посмотреть другим? Почему мне понравились конкретные экспонаты, и как я отношусь к технологиям будущего?. Задавай мне на английском языке вопросы по этой теме, последовательно, один вопрос за другим, следующий вопрос задавай только после моего ответа на предыдущий вопрос. Ты можешь исправлять меня, если я неправильно отвечаю и допускаю ошибки в английском языке."
            #content = "Представь, что ты преподаватель обществознания, а я твой ученик."
        )
    ],
    temperature = 0.7,
    max_tokens = 300,
)
# ============================ speechkit ============================
session = Session.from_yandex_passport_oauth_token(oauth_token, catalog_id)

# Создаем экземляр класса `SpeechSynthesis`, передавая `session`,
# который уже содержит нужный нам IAM-токен
# и другие необходимые для API реквизиты для входа
synthesizeAudio = SpeechSynthesis(session)

def pyaudio_play_audio_function(audio_data, num_channels=1,
                                sample_rate=16000, chunk_size=4000) -> None:
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=num_channels,
        rate=sample_rate,
        output=True,
        frames_per_buffer=chunk_size
    )

    try:
        for i in range(0, len(audio_data), chunk_size):
            stream.write(audio_data[i:i + chunk_size])
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

sample_rate = 16000
chat = False
start_chat_msgs = ['поговорим на английском', 'говорим на английском', 'английском', 'поговорим на русском', 'говорим на русском', 'русском',]
russian = 'русском'
english = 'английском'
in_english = False
russian_voice = 'zahar'
english_voice = 'john'

giga = GigaChat(credentials=gigachat_creds, verify_ssl_certs=False, model="GigaChat-Pro")
# ===================================================================

try:
    model = vosk.Model(r"C:\your_path\vosk-model-ru")
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=dev_id, dtype='int16', channels=1, callback=(lambda i, f, t, s: q.put(bytes(i)))):
        rec = vosk.KaldiRecognizer(model, samplerate)

        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())["text"]
                print("Recognized: " + data)
                if data:
                    if chat == False:
                        if any(start in data for start in start_chat_msgs):
                            # start new chat
                            chat = True
                            if english in data:
                                voice = english_voice
                                model = vosk.Model(r"C:\your_path\vosk-model-en")
                                with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=dev_id, dtype='int16', channels=1, callback=(lambda i, f, t, s: q.put(bytes(i)))):
                                    rec = vosk.KaldiRecognizer(model, samplerate)
                                audio_data = synthesizeAudio.synthesize_stream(
                                    text = "sure, let's talk" + '.0.',
                                    voice = voice, format = 'lpcm', sampleRateHertz = sample_rate)
                                pyaudio_play_audio_function(audio_data, sample_rate = sample_rate)
                                q.queue.clear()
                                start = time.time()
                            else:
                                voice = russian_voice
                                audio_data = synthesizeAudio.synthesize_stream(
                                    text = 'хорошо, давайте попробуем' + '.0.',
                                    voice = voice, format = 'lpcm', sampleRateHertz = sample_rate)
                                pyaudio_play_audio_function(audio_data, sample_rate = sample_rate)
                                q.queue.clear()
                                start = time.time()
                    else:
                        payload.messages.append(Messages(role=MessagesRole.USER, content=data))
                        response = giga.chat(payload)
                        reply = response.choices[0].message.content
                        print(f"GigaChat: {reply}")
                        payload.messages.append(response.choices[0].message)

                        audio_data = synthesizeAudio.synthesize_stream(
                            text = reply + '.0.', voice = voice, format = 'lpcm', sampleRateHertz = sample_rate)
                        pyaudio_play_audio_function(audio_data, sample_rate = sample_rate)
                        q.queue.clear()
                        start = time.time()

            else:
                data = json.loads(rec.PartialResult())["partial"]
                if chat == True:
                    end = time.time()
                    if end - start > 30:
                        if in_english:
                            text = 'New chat'
                        else:
                            text = 'Новый чат'
                        audio_data = synthesizeAudio.synthesize_stream(
                                text = text, voice = voice, format = 'lpcm', sampleRateHertz = sample_rate)
                        pyaudio_play_audio_function(audio_data, sample_rate = sample_rate)
                        q.queue.clear()
                        chat = False


except KeyboardInterrupt:
    print('\nDone')



