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
                # Render through SAPI synchronously: pyttsx3's async file helper
                # closed its WAV early, and this runner lacks System.Speech.dll.
                from comtypes.client import CreateObject
                speaker=CreateObject('SAPI.SpVoice')
                tokens=speaker.GetVoices()
                allowed=[tokens.Item(i) for i in range(tokens.Count) if not re.search('asad|uzma',tokens.Item(i).GetDescription(),re.I)]
                if not allowed:raise RuntimeError('No allowed SAPI voice')
                speaker.Voice=allowed[0]
                stream=CreateObject('SAPI.SpFileStream')
                stream.Open(str(audio),3)
                try:
                    speaker.AudioOutputStream=stream
                    speaker.Speak('Hello Nexus, please check the processor and memory usage on my computer.',0)
                finally:stream.Close()
                result['synthesis_backend']='SAPI synchronous file output'
                result['sapi_file_synthesis']=audio.is_file() and audio.stat().st_size>44
                if result['sapi_file_synthesis']:
                    recognizer=sr.Recognizer();recognizer.operation_timeout=6
                    with sr.AudioFile(str(audio)) as source:clip=recognizer.record(source)
                    import audioop
                    raw=clip.get_raw_data(convert_rate=16000,convert_width=2)
                    result['synthetic_signal']={'duration_seconds':round(len(raw)/32000,2),'rms_pcm16':audioop.rms(raw,2)}
                    result['sapi_file_synthesis']=len(raw)>16000 and audioop.rms(raw,2)>0
                    normalized=sr.AudioData(raw,16000,2)
                    try:
                        text=recognizer.recognize_google(normalized,language='en-IN',endpoint='https://www.google.com/speech-api/v2/recognize')
                        result['google_en_IN_synthetic']={'status':'response','text':text}
                    except Exception as exc:result['google_en_IN_synthetic']={'status':'unavailable','error_type':type(exc).__name__}
        finally:engine.stop()
    except Exception as exc:
        result.setdefault('windows_sapi',{'initialized':False})
        result['sapi_probe_error']=type(exc).__name__
    try:
        from nexus.tts import edge_audio
        data=asyncio.run(edge_audio('NEXUS voice connection test.'))
        result['edge_prabhat']={'status':'audio received','bytes':len(data)}
    except Exception as exc:result['edge_prabhat']={'status':'unavailable','error_type':type(exc).__name__}
    # Only generated test text/component results; no credentials or microphone audio.
    print('::notice::VOICE_PROBE '+json.dumps(result,ensure_ascii=True))

if __name__=='__main__':main()
