
import pyttsx3

engine = pyttsx3.init(driverName='espeak')
engine.setProperty('voice', 'pt+m1')

def say(text):
    engine.say(text)
    engine.runAndWait()
