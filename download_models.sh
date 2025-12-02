#!/bin/bash

mkdir -p models/vosk-en
mkdir -p models/vosk-ru

echo "Downloading English Vosk model..."
wget https://alphacephei.com/vosk/models/vosk-model-en-0.22.zip -O models/vosk-en/model.zip
unzip models/vosk-en/model.zip -d models/vosk-en
rm models/vosk-en/model.zip

echo "Downloading Russian Vosk model..."
wget https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip -O models/vosk-ru/model.zip
unzip models/vosk-ru/model.zip -d models/vosk-ru
rm models/vosk-ru/model.zip

echo "✅ Speech models installed!"
