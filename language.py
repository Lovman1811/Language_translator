# app.py
from flask import Flask, render_template, request, jsonify, send_file
from googletrans import Translator
from gtts import gTTS
import os
import speech_recognition as spr
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/audio'

# Create audio directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Language mapping (language name to language code)
LANGUAGE_MAP = {
    'Afrikaans': 'af', 'Albanian': 'sq', 'Arabic': 'ar', 'Armenian': 'hy',
    'Azerbaijani': 'az', 'Basque': 'eu', 'Belarusian': 'be', 'Bengali': 'bn',
    'Bosnian': 'bs', 'Bulgarian': 'bg', 'Catalan': 'ca', 'Cebuano': 'ceb',
    'Chinese': 'zh', 'Corsican': 'co', 'Croatian': 'hr', 'Czech': 'cs',
    'Danish': 'da', 'Dutch': 'nl', 'English': 'en', 'Esperanto': 'eo',
    'Estonian': 'et', 'Finnish': 'fi', 'French': 'fr', 'Frisian': 'fy',
    'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el',
    'Gujarati': 'gu', 'Haitian Creole': 'ht', 'Hausa': 'ha', 'Hawaiian': 'haw',
    'Hebrew': 'he', 'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu',
    'Icelandic': 'is', 'Igbo': 'ig', 'Indonesian': 'id', 'Irish': 'ga',
    'Italian': 'it', 'Japanese': 'ja', 'Javanese': 'jv', 'Kannada': 'kn',
    'Kazakh': 'kk', 'Khmer': 'km', 'Kinyarwanda': 'rw', 'Korean': 'ko',
    'Kurdish': 'ku', 'Kyrgyz': 'ky', 'Lao': 'lo', 'Latin': 'la', 'Latvian': 'lv',
    'Lithuanian': 'lt', 'Luxembourgish': 'lb', 'Macedonian': 'mk', 'Malagasy': 'mg',
    'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt', 'Maori': 'mi',
    'Marathi': 'mr', 'Mongolian': 'mn', 'Myanmar': 'my', 'Nepali': 'ne',
    'Norwegian': 'no', 'Odia': 'or', 'Pashto': 'ps', 'Persian': 'fa',
    'Polish': 'pl', 'Portuguese': 'pt', 'Punjabi': 'pa', 'Romanian': 'ro',
    'Russian': 'ru', 'Samoan': 'sm', 'Scots Gaelic': 'gd', 'Serbian': 'sr',
    'Sesotho': 'st', 'Shona': 'sn', 'Sindhi': 'sd', 'Sinhala': 'si',
    'Slovak': 'sk', 'Slovenian': 'sl', 'Somali': 'so', 'Spanish': 'es',
    'Sundanese': 'su', 'Swahili': 'sw', 'Swedish': 'sv', 'Tajik': 'tg',
    'Tamil': 'ta', 'Tatar': 'tt', 'Telugu': 'te', 'Thai': 'th', 'Turkish': 'tr',
    'Turkmen': 'tk', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Uyghur': 'ug',
    'Uzbek': 'uz', 'Vietnamese': 'vi', 'Welsh': 'cy', 'Xhosa': 'xh',
    'Yiddish': 'yi', 'Yoruba': 'yo', 'Zulu': 'zu'
}

# Language options for dropdowns
LANGUAGES = [
    'Auto Detect', 'Afrikaans', 'Albanian', 'Arabic', 'Armenian', 'Azerbaijani',
    'Basque', 'Belarusian', 'Bengali', 'Bosnian', 'Bulgarian', 'Catalan',
    'Cebuano', 'Chinese', 'Corsican', 'Croatian', 'Czech', 'Danish', 'Dutch',
    'English', 'Esperanto', 'Estonian', 'Finnish', 'French', 'Frisian',
    'Galician', 'Georgian', 'German', 'Greek', 'Gujarati', 'Haitian Creole',
    'Hausa', 'Hawaiian', 'Hebrew', 'Hindi', 'Hmong', 'Hungarian', 'Icelandic',
    'Igbo', 'Indonesian', 'Irish', 'Italian', 'Japanese', 'Javanese', 'Kannada',
    'Kazakh', 'Khmer', 'Kinyarwanda', 'Korean', 'Kurdish', 'Kyrgyz', 'Lao',
    'Latin', 'Latvian', 'Lithuanian', 'Luxembourgish', 'Macedonian', 'Malagasy',
    'Malay', 'Malayalam', 'Maltese', 'Maori', 'Marathi', 'Mongolian', 'Myanmar',
    'Nepali', 'Norwegian', 'Odia', 'Pashto', 'Persian', 'Polish', 'Portuguese',
    'Punjabi', 'Romanian', 'Russian', 'Samoan', 'Scots Gaelic', 'Serbian',
    'Sesotho', 'Shona', 'Sindhi', 'Sinhala', 'Slovak', 'Slovenian', 'Somali',
    'Spanish', 'Sundanese', 'Swahili', 'Swedish', 'Tajik', 'Tamil', 'Tatar',
    'Telugu', 'Thai', 'Turkish', 'Turkmen', 'Ukrainian', 'Urdu', 'Uyghur',
    'Uzbek', 'Vietnamese', 'Welsh', 'Xhosa', 'Yiddish', 'Yoruba', 'Zulu'
]


@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES, language_map=LANGUAGE_MAP)


@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    lang = data.get('lang')

    if not text:
        return jsonify({'error': 'Please enter text to translate'}), 400

    try:
        translator = Translator()
        if lang == 'Auto Detect':
            # Auto detect source language
            result = translator.translate(text)
            translated_text = result.text
            detected_lang = result.src
        else:
            # Translate to specific language
            lang_code = LANGUAGE_MAP.get(lang, 'en')
            translated_text = translator.translate(text, dest=lang_code).text
            detected_lang = lang

        return jsonify({
            'translated_text': translated_text,
            'detected_lang': detected_lang
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text')
    lang = data.get('lang')

    if not text:
        return jsonify({'error': 'No text to speak'}), 400

    lang_code = LANGUAGE_MAP.get(lang, 'en')

    try:
        # Generate unique filename
        filename = f"tts_{int(time.time())}.mp3"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Generate speech
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(filepath)

        return jsonify({'audio_file': f'/static/audio/{filename}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    try:
        # Save temporary audio file
        temp_filename = f"stt_{int(time.time())}.wav"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        audio_file.save(temp_path)

        # Recognize speech
        recognizer = spr.Recognizer()
        with spr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Clean up temporary file
        os.remove(temp_path)

        return jsonify({'text': text})

    except spr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio'}), 400
    except spr.RequestError as e:
        return jsonify({'error': f'Speech recognition service error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
