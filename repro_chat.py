import json
import sys
import uuid
from urllib import error, request

BASE = 'http://127.0.0.1:8000/api'

boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
text = 'Hello world, this is a sample document.'
body = []
body.append('--' + boundary)
body.append('Content-Disposition: form-data; name="file"; filename="sample.txt"')
body.append('Content-Type: text/plain\r\n')
body.append(text)
body.append('--' + boundary + '--\r\n')
body_bytes = '\r\n'.join(body).encode('utf-8')
req = request.Request(
    f'{BASE}/documents',
    data=body_bytes,
    headers={'Content-Type': 'multipart/form-data; boundary=' + boundary},
)
try:
    with request.urlopen(req) as res:
        body = res.read().decode()
        print('UPLOAD STATUS', res.status)
        print(body)
        data = json.loads(body)
except error.HTTPError as e:
    print('UPLOAD ERROR', e.code, e.read().decode(), file=sys.stderr)
    sys.exit(1)

chat_body = json.dumps({
    'document_id': data['id'],
    'messages': [{'role': 'user', 'content': 'What is in this document?'}],
}).encode('utf-8')
chat_req = request.Request(
    f'{BASE}/chat',
    data=chat_body,
    headers={'Content-Type': 'application/json'},
)
try:
    with request.urlopen(chat_req) as res:
        body = res.read().decode()
        print('CHAT STATUS', res.status)
        print(body)
except error.HTTPError as e:
    print('CHAT ERROR', e.code, e.read().decode(), file=sys.stderr)
    sys.exit(1)
