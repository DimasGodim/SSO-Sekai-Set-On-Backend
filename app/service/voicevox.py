import requests

def request_audio(text: str, speaker_id: int):
    try:
        url = 'https://api.tts.quest/v3/voicevox/synthesis/'
        params = {
            'speaker': speaker_id, 
            'text': text
        }
        response = requests.get(url, params=params)
        data = response.json()
        download = data.get('mp3DownloadUrl')
        streaming = data.get('mp3StreamingUrl') 
        return {
            'status': True,
            'download_audio': download,
            'streaming_audio': streaming
        }
    
    except Exception as e:
        return {
            'status': False,
            'penyebab': str(e)
        }

def normalize(text: str) -> str:
    return text.strip().lower()