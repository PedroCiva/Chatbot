import pyttsx3
from googletrans import Translator, constants
from pprint import pprint

# This script takes care of the text translation and conversion from Text to Speech

engine = pyttsx3.init()

voices = engine.getProperty('voices')

# List of available languages installed on this computer
languages = []
start = "- "
end = "("

def list_voices():
    print("List of available voices and languages:  \n")
    for voice in voices:
        # Extract the name of the language only
        languange_string = voice.name
        languages.append((languange_string.split(start))[1].split(end)[0])
        print("Language: " + (languange_string.split(start))[1].split(end)[0])
        print("ID: " + voice.id + "\n")



def change_voice(voice_id):
    for voice in engine.getProperty('voices'):
        if voice_id in voice.id:
            engine.setProperty('voice', voice.id)
            return True

    # raise RuntimeError("Language '{}' for gender '{}' not found".format(language, gender))

def Say(text):
    engine.say(text)
    engine.runAndWait()


# init the Google API translator
translator = Translator()

# Currently translating from english to french, id for french = 'fr', id for english = 'en'
def Translate(sentence, id):
    translation = translator.translate(sentence, dest=id)
    return str(translation.text)
