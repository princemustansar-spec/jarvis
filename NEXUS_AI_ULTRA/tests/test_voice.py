"""Offline voice contracts. Hardware/model doubles are explicitly identified."""
import asyncio
import hashlib
import importlib
import json
import math
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest
from fastapi.testclient import TestClient
import nexus.voice as v


@pytest.fixture
def voice_client(tmp_path,monkeypatch):
    monkeypatch.setenv('NEXUS_DATA_DIR',str(tmp_path))
    import nexus.app
    m=importlib.reload(nexus.app)
    with TestClient(m.app) as c:
        c.headers['x-nexus-token']=c.get('/api/state').json()['token']
        yield c,m


def verified_model(tmp_path):
    tmp_path.mkdir(parents=True,exist_ok=True)
    files={n:b'test fixture only' for n in ('model.bin','config.json','tokenizer.json')}
    for name,data in files.items():(tmp_path/name).write_bytes(data)
    (tmp_path/'verified.json').write_text(json.dumps({'repo':v.MODEL_REPO,'files':{n:hashlib.sha256(d).hexdigest() for n,d in files.items()}}))
    return tmp_path


def test_checksum_sha256_and_git_blob(tmp_path):
    p=tmp_path/'file';p.write_bytes(b'abc')
    sha=hashlib.sha256(b'abc').hexdigest()
    assert v.verify_download(p,sha)==sha
    assert v.verify_download(p,hashlib.sha1(b'blob 3\0abc').hexdigest())==sha
    with pytest.raises(ValueError,match='mismatch'):v.verify_download(p,'0'*64)
    with pytest.raises(ValueError,match='checksum'):v.verify_download(p,'untrusted')


def test_model_manifest_detects_tampering(tmp_path):
    p=verified_model(tmp_path/'tiny');assert v.model_manifest(p,True)
    (p/'model.bin').write_bytes(b'changed')
    assert v.model_manifest(p,True) is None


def test_install_pins_revision_and_verifies_every_artifact(tmp_path,monkeypatch):
    import huggingface_hub as hf
    data={n:b'checked fixture '+n.encode() for n in ('config.json','model.bin','tokenizer.json','vocabulary.txt')}
    revision='a'*40
    monkeypatch.setattr(hf,'HfApi',lambda:SimpleNamespace(model_info=lambda repo:SimpleNamespace(sha=revision,siblings=[SimpleNamespace(rfilename=n) for n in data])))
    monkeypatch.setattr(hf,'hf_hub_url',lambda repo,name,revision:f'https://test/{revision}/{name}')
    monkeypatch.setattr(hf,'get_hf_file_metadata',lambda url:SimpleNamespace(etag=hashlib.sha256(data[url.split('/')[-1]]).hexdigest()))
    def download(repo,name,revision,local_dir):
        assert repo==v.MODEL_REPO and revision=='a'*40
        p=Path(local_dir)/name;p.write_bytes(data[name]);return str(p)
    monkeypatch.setattr(hf,'hf_hub_download',download)
    p=tmp_path/'tiny';result=v.install_model(p,Mock())
    assert result['verified'] and v.model_manifest(p,True)['revision']==revision
    assert v.install_model(p,Mock())['already_installed']


def test_install_rejects_checksum_failure_and_leaves_no_active_model(tmp_path,monkeypatch):
    import huggingface_hub as hf
    monkeypatch.setattr(hf,'HfApi',lambda:SimpleNamespace(model_info=lambda repo:SimpleNamespace(sha='a'*40,siblings=[SimpleNamespace(rfilename=n) for n in ('config.json','model.bin','tokenizer.json')])))
    monkeypatch.setattr(hf,'get_hf_file_metadata',lambda url:SimpleNamespace(etag='0'*64))
    def download(repo,name,revision,local_dir):
        p=Path(local_dir)/name;p.write_bytes(b'bad');return str(p)
    monkeypatch.setattr(hf,'hf_hub_download',download)
    with pytest.raises(ValueError,match='checksum mismatch'):v.install_model(tmp_path/'tiny',Mock())
    assert not (tmp_path/'tiny').exists() and not (tmp_path/'.tiny-download').exists()


class InputDouble:
    def __init__(self,signal=.1,stop=None):self.signal=signal;self.stop=stop;self.reads=0
    def query_devices(self,device=None,kind=None):return {'default_samplerate':48000,'max_input_channels':1}
    def check_input_settings(self,**kwargs):assert kwargs['channels']==1 and kwargs['samplerate']==48000
    def InputStream(self,**kwargs):return self
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,frames):
        self.reads+=1
        if self.stop:self.stop.set()
        return np.full((frames,1),self.signal,dtype=np.float32),False


def test_record_uses_native_rate_bounded_frames_and_reports_signal():
    sd=InputDouble();audio,rate,m=v.record_audio(sd,None,2,threading.Event(),Mock())
    assert rate==48000 and len(audio)==96000 and not m['silence'] and m['permission_tested']
    assert abs(m['level_dbfs']+20)<.1


def test_stop_capture_ends_early_without_discarding():
    stop=threading.Event();sd=InputDouble(stop=stop)
    audio,rate,m=v.record_audio(sd,None,15,stop,Mock())
    assert sd.reads==1 and len(audio)==1024


def test_silence_and_clipping_metrics():
    _,_,silence=v.record_audio(InputDouble(0),None,2,threading.Event(),Mock())
    _,_,clipped=v.record_audio(InputDouble(1),None,2,threading.Event(),Mock())
    assert silence['silence'] and clipped['clipping']


def test_roman_urdu_real_transliteration_is_latin_and_english_unchanged():
    assert v.romanize('Hello, check my CPU')=='Hello, check my CPU'
    converted=v.romanize('میرا نام علی ہے')
    assert converted and not any('\u0600'<=c<='\u06ff' for c in converted)


def test_transcriber_cpu_int8_local_only_and_no_auto_send(tmp_path,monkeypatch):
    calls={}
    class ModelDouble:
        def __init__(self,*args,**kwargs):calls.update(kwargs)
        def transcribe(self,audio,**kwargs):
            assert isinstance(audio,np.ndarray) and len(audio)==16000 and audio.dtype==np.float32
            assert kwargs['beam_size']==1 and kwargs['vad_filter'] and kwargs['language']=='en'
            return [SimpleNamespace(text='Controlled transport fixture')],SimpleNamespace(language='en')
    monkeypatch.setitem(sys.modules,'faster_whisper',SimpleNamespace(WhisperModel=ModelDouble))
    r=v.transcribe_audio(np.full(48000,.1),48000,tmp_path,'en',Mock())
    assert r['text']=='Controlled transport fixture' and r['offline']
    assert calls['device']=='cpu' and calls['compute_type']=='int8' and calls['local_files_only'] and calls['num_workers']==1 and calls['cpu_threads']<=2


def test_diagnostics_enumeration_is_not_permission_claim():
    sd=SimpleNamespace(query_devices=lambda:[{'name':'Mic','max_input_channels':1,'hostapi':0,'default_samplerate':48000},{'name':'Output','max_input_channels':0}],query_hostapis=lambda:[{'name':'WASAPI'}],default=SimpleNamespace(device=(0,1)))
    r=v.enumerate_inputs(sd);assert len(r['devices'])==1 and r['devices'][0]['host_api']=='WASAPI' and not r['permission_tested']


def test_worker_missing_model_does_not_open_microphone(tmp_path,monkeypatch):
    sd=Mock();monkeypatch.setitem(sys.modules,'sounddevice',sd);pipe=Mock()
    v.voice_worker(pipe,threading.Event(),'capture',{'device':None,'language':'en','seconds':5},str(tmp_path/'missing'))
    assert pipe.send.call_args.args[0]['phase']=='error'
    sd.InputStream.assert_not_called()


@pytest.mark.parametrize('options',[{'device':-1},{'device':True},{'seconds':16},{'seconds':float('nan')},{'seconds':True},{'language':'bad'}])
def test_service_rejects_invalid_input_without_spawning(tmp_path,options):
    with pytest.raises(ValueError):v.VoiceService(tmp_path).start('capture',**options)


def test_real_spawn_diagnostics_or_explicit_platform_error_releases_worker(tmp_path):
    service=v.VoiceService(tmp_path)
    try:
        service.start('diagnostics')
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            status=service.status()
            if status['phase'] in ('done','error'):break
            time.sleep(.05)
        assert status['phase'] in ('done','error')
        if status['phase']=='done':assert 'devices' in status['result']
        else:assert status['error']  # Cloud has no PortAudio/microphone; this is not hardware acceptance.
        for _ in range(50):
            service.status()
            if service.process is None:break
            time.sleep(.02)
        assert service.process is None
    finally:service.cancel()


def test_api_requires_consent_and_keeps_existing_history(voice_client,monkeypatch):
    c,m=voice_client
    start=Mock(return_value={'job_id':'job','phase':'starting'});monkeypatch.setattr(m.voice,'start',start)
    assert c.post('/api/voice/start',json={}).status_code==400
    assert c.post('/api/voice/test',json={}).status_code==400
    assert c.post('/api/voice/model',json={}).status_code==400
    start.assert_not_called()
    assert c.post('/api/voice/start',json={'consent':True,'language':'ur','seconds':5,'device':None}).status_code==200
    assert c.get('/api/state').json()['voice_settings']['language']=='ur'
    assert c.get('/api/state').json()['chat']==[]
    assert c.post('/api/voice/start',json={'consent':True},headers={'x-nexus-token':'wrong'}).status_code==403


def test_emergency_stop_cancels_voice_and_rejects_recording(voice_client,monkeypatch):
    c,m=voice_client;cancel=Mock(return_value={'cancelled':True});monkeypatch.setattr(m.voice,'cancel',cancel)
    c.post('/api/safety',json={'stop':True});cancel.assert_called_once()
    assert c.post('/api/voice/start',json={'consent':True}).status_code==400
    assert c.post('/api/voice/test',json={'consent':True}).status_code==400


def test_stop_and_cancel_routes(voice_client,monkeypatch):
    c,m=voice_client
    monkeypatch.setattr(m.voice,'stop_recording',lambda:{'stopping':True})
    assert c.post('/api/voice/stop',json={}).json()['stopping']
    assert c.post('/api/voice/cancel',json={}).json()['cancelled']


def test_cancel_terminates_only_owned_worker_and_releases_handle(tmp_path):
    service=v.VoiceService(tmp_path)
    process=service.context.Process(target=time.sleep,args=(20,),daemon=True)
    process.start();service.process=process
    service.state={'phase':'transcribing','job_id':'owned'}
    try:
        assert service.cancel()['cancelled']
        assert service.process is None and service.state['phase']=='cancelled'
    finally:
        if service.process:service.cancel()
