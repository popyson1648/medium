import os
import requests
import json
import re
from typing import Dict, Union, List
from functools import wraps

# Medium APIトークン
token = 'mytoken'
base_url = 'https://api.medium.com/v1'

# ヘッダーの設定
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Charset': 'utf-8'
}

def debug_mode(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.getenv('DEBUG'):
            project_root = os.path.dirname(os.path.abspath(__file__))
            os.environ['GITHUB_EVENT_PATH'] = os.path.join(project_root, 'event.json')
        return func(*args, **kwargs)
    return wrapper

def get_user_id() -> str:
    response = requests.get(f'{base_url}/me', headers=headers)
    try:
        response.raise_for_status()  # HTTPエラーチェック
        user_info = response.json()
        print(user_info)  # デバッグ用にレスポンス全体を表示
        return user_info['data']['id']
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
    except json.JSONDecodeError:
        print('Error decoding JSON response')
        print(f'Response content: {response.content}')  # レスポンスの内容を表示
    return ''  # エラー時は空文字を返す

def parse_metadata(content: str) -> Dict[str, str]:
    metadata = {}
    match = re.search(r'<!--(.*?)-->', content, re.DOTALL)
    if match:
        metadata_block = match.group(1).strip()
        for line in metadata_block.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
    return metadata

@debug_mode
def read_event_data() -> Dict:
    event_path = os.getenv('GITHUB_EVENT_PATH')
    with open(event_path, 'r') as f:
        return json.load(f)

def post_to_medium(user_id: str, post_data: Dict[str, Union[str, List[str], bool]]) -> None:
    response = requests.post(
        f'{base_url}/users/{user_id}/posts', headers=headers, json=post_data)
    try:
        response.raise_for_status()  # HTTPエラーチェック
        print(f'Successfully posted to Medium: {response.json()}')
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
    except json.JSONDecodeError:
        print('Error decoding JSON response')
        print(f'Response content: {response.content}')  # レスポンスの内容を表示

def main() -> None:
    user_id = get_user_id()
    if not user_id:
        print("Failed to retrieve user ID. Exiting...")
        return

    event_data = read_event_data()

    for commit in event_data['commits']:
        added_files = commit.get('added', [])
        modified_files = commit.get('modified', [])
        for file_path in added_files + modified_files:
            if file_path.startswith('articles/') and file_path.endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                metadata = parse_metadata(content)
                title = metadata.get('title', 'Untitled')
                tags = [tag.strip() for tag in metadata.get('tags', '').split(',')]
                publish_status = metadata.get('publishStatus', 'draft')
                license = metadata.get('license', '')
                notify_followers = metadata.get('notifyFollowers', 'false').lower() == 'true'

                content = re.sub(r'<!--(.*?)-->', '', content, count=1, flags=re.DOTALL).strip()

                post_data = {
                    'title': title,
                    'contentFormat': 'markdown',
                    'content': content,
                    'tags': tags,
                    'publishStatus': publish_status,
                    'license': license,
                    'notifyFollowers': notify_followers
                }

                post_to_medium(user_id, post_data)

if __name__ == '__main__':
    main()
