import os
import requests
import json
import re
import logging
from typing import Dict, Union, List
from functools import wraps

# Medium APIトークン
token = os.getenv('MEDIUM_API_TOKEN')
base_url = 'https://api.medium.com/v1'

# ヘッダーの設定
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Charset': 'utf-8'
}

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f'Entering: {func.__name__}')
        result = func(*args, **kwargs)
        logging.info(f'Exiting: {func.__name__}')
        return result
    return wrapper

@log_function
def get_user_id() -> str:
    response = requests.get(f'{base_url}/me', headers=headers)
    try:
        response.raise_for_status()  # HTTPエラーチェック
        user_info = response.json()
        logging.info(f'User info: {user_info}')  # デバッグ用にレスポンス全体を表示
        return user_info['data']['id']
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except json.JSONDecodeError:
        logging.error('Error decoding JSON response')
        logging.error(f'Response content: {response.content}')  # レスポンスの内容を表示
    return ''  # エラー時は空文字を返す

@log_function
def parse_metadata(content: str) -> Dict[str, str]:
    metadata = {}
    match = re.search(r'<!--(.*?)-->', content, re.DOTALL)
    if match:
        metadata_block = match.group(1).strip()
        for line in metadata_block.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
    logging.info(f'Metadata parsed: {metadata}')
    return metadata

@log_function
def post_to_medium(user_id: str, post_data: Dict[str, Union[str, List[str], bool]]) -> None:
    response = requests.post(
        f'{base_url}/users/{user_id}/posts', headers=headers, json=post_data)
    try:
        response.raise_for_status()  # HTTPエラーチェック
        logging.info(f'Successfully posted to Medium: {response.json()}')
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except json.JSONDecodeError:
        logging.error('Error decoding JSON response')
        logging.error(f'Response content: {response.content}')  # レスポンスの内容を表示

@log_function
def main() -> None:
    user_id = get_user_id()
    if not user_id:
        logging.error("Failed to retrieve user ID. Exiting...")
        return

    changed_files = os.getenv('changed_files')
    if not changed_files:
        logging.error("No changed files found. Exiting...")
        return

    md_files = changed_files.split(',')

    for file_path in md_files:
        logging.info(f'Processing file: {file_path}')
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
