import pyttsx3

engine = pyttsx3.init(driverName='fala')

# rate = engine.getProperty('rate')
# engine.setProperty('rate', rate+50)
# pitch = engine.getProperty('espeak.PITCH')
# engine.setProperty('pitch', pitch+5)
engine.setProperty('voice', 'pt+m1')
engine.say('Oi, eu sou o Batman, e eu moro na cidade de gótam e vou matar o coringa')
engine.runAndWait()

# voices = engine.getProperty('voices')
# for voice in voices:
#     engine.setProperty('voice', voice.id)
#     engine.say('The quick brown fox jumped over the lazy dog.')
#     engine.runAndWait()
