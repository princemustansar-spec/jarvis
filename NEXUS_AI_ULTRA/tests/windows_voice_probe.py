"""Windows CI diagnostics, never a physical microphone/speaker acceptance claim."""
import asyncio
import json
from pathlib import Path
import re
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))


def main():
    result={'platform':sys.platform,'physical_microphone_tested':False,'speaker_playback_tested':False}
    if sys.platform!='win32':
        print(json.dumps({**result,'status':'not Windows'}));return
    try:
        import pyttsx3
        import speech_recognition as sr
        engine=pyttsx3.init('sapi5')
        try:
            voices=[v for v in engine.getProperty('voices') if not re.search('asad|uzma',v.name+' '+v.id,re.I)]
            if not voices:raise RuntimeError('No allowed SAPI voice')
            engine.setProperty('voice',voices[0].id)
            result['windows_sapi']={'initialized':True,'allowed_voice_count':len(voices)}
            with tempfile.TemporaryDirectory(prefix='nexus-sapi-probe-') as folder:
                audio=Path(folder)/'synthetic.wav'
                engine.save_to_file('NEXUS CPU memory check.',str(audio));engine.runAndWait()
                result['sapi_file_synthesis']=audio.is_file() and audio.stat().st_size>44
                if result['sapi_file_synthesis']:
                    recognizer=sr.Recognizer();recognizer.operation_timeout=6
                    with sr.AudioFile(str(audio)) as source:clip=recognizer.record(source)
                    try:
                        text=recognizer.recognize_google(clip,language='en-IN',endpoint='https://www.google.com/speech-api/v2/recognize')
                        result['google_en_IN_synthetic']={'status':'response','text':text}
                    except Exception as exc:result['google_en_IN_synthetic']={'status':'unavailable','error_type':type(exc).__name__}
        finally:engine.stop()
    except Exception as exc:result['windows_sapi']={'initialized':False,'error_type':type(exc).__name__}
    try:
        from nexus.tts import edge_audio
        data=asyncio.run(edge_audio('NEXUS voice connection test.'))
        result['edge_prabhat']={'status':'audio received','bytes':len(data)}
    except Exception as exc:result['edge_prabhat']={'status':'unavailable','error_type':type(exc).__name__}
    # Only generated test text/component results; no credentials or microphone audio.
    print('::notice::VOICE_PROBE '+json.dumps(result,ensure_ascii=True))

if __name__=='__main__':main()
