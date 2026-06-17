import json
import urllib.request
from urllib.error import HTTPError

BASE = 'http://127.0.0.1:8000'

# Set these to an EXISTING Django user account + its real password
# NOTE: The token endpoint will return 401 if the password is wrong.
USERNAME = 'doctor0'
PASSWORD = 'REPLACE_WITH_REAL_PASSWORD'



def post_json(url, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    return urllib.request.urlopen(req).read()


def get_with_bearer(url, token):
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    return urllib.request.urlopen(req).read()


try:
    token_resp = post_json(f'{BASE}/api/token/', {'username': USERNAME, 'password': PASSWORD})
    tokens = json.loads(token_resp.decode('utf-8'))
    access = tokens['access']
    print('Obtained access token')

    patients_resp = get_with_bearer(f'{BASE}/api/patients/', access)
    print('GET /api/patients/ with JWT OK, response starts:')
    print(patients_resp[:200])

except HTTPError as e:
    print('HTTPError:', e.code)
    try:
        print(e.read().decode('utf-8'))
    except Exception:
        pass

