"""Thin client for official ACE-Step 1.5 HTTP API.
Endpoints: POST /release_task, POST /query_result, GET /v1/audio.
"""
import json
import time
from urllib.parse import urljoin, urlparse
import requests

class AceStepError(RuntimeError):
    pass

class AceClient:
    def __init__(self, base_url: str, token: str = ''):
        base_url = base_url.strip().rstrip('/')
        parsed = urlparse(base_url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            raise AceStepError('ACE-Step 서버 주소가 잘못됐습니다. http(s)://주소:포트 형태로 입력하세요.')
        self.base_url = base_url
        self.session = requests.Session()
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'

    def _request(self, method, endpoint, **kwargs):
        try:
            response = self.session.request(method, urljoin(self.base_url+'/', endpoint.lstrip('/')), timeout=kwargs.pop('timeout', 25), **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as ex:
            raise AceStepError(f'ACE-Step 서버 요청 실패: {ex}') from ex

    @staticmethod
    def _data(response):
        try:
            body = response.json()
        except ValueError as ex:
            raise AceStepError('서버가 JSON이 아닌 응답을 반환했습니다.') from ex
        if body.get('code', 200) != 200 or body.get('error'):
            raise AceStepError(str(body.get('error') or body))
        return body.get('data', body)

    def health(self):
        return self._data(self._request('GET', '/health'))

    def generate(self, prompt, lyrics, duration=30, vocal=True):
        payload = {
            'prompt': prompt,
            'lyrics': lyrics if vocal else '',
            'audio_duration': duration,
            'audio_format': 'mp3',
            'inference_steps': 8,
            'batch_size': 1,
            'thinking': False,
            'use_format': False,
            'vocal_language': 'ko' if vocal else 'en',
        }
        data = self._data(self._request('POST', '/release_task', json=payload, timeout=45))
        task_id = data.get('task_id') if isinstance(data, dict) else None
        if not task_id:
            raise AceStepError(f'생성 작업 ID를 받지 못했습니다: {data}')
        return task_id

    def query(self, task_id):
        data = self._data(self._request('POST', '/query_result', json={'task_id_list': [task_id]}, timeout=30))
        if not isinstance(data, list) or not data:
            return {'status': 0, 'files': []}
        item = data[0]
        status = int(item.get('status', 0))
        raw_result = item.get('result') or '[]'
        try:
            files = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
        except (TypeError, ValueError):
            files = []
        return {'status': status, 'files': files if isinstance(files, list) else [], 'error': item.get('error')}

    def fetch_audio(self, file_path):
        # Only allow relative paths returned by the chosen ACE-Step server.
        # Do not follow arbitrary external URLs embedded in a task result.
        if not isinstance(file_path, str) or not file_path.startswith('/v1/audio?'):
            raise AceStepError('지원하지 않는 오디오 다운로드 경로입니다.')
        response = self._request('GET', file_path, timeout=90, allow_redirects=False)
        if not response.content:
            raise AceStepError('음원 파일이 비어 있습니다.')
        return response.content
