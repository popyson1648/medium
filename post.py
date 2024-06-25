import os
import requests
import json
import re

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

def get_user_id() -> str:
    response = requests.get(f'{base_url}/me', headers=headers)
    user_info = response.json()
    return user_info['data']['id']

def parse_metadata(content: str) -> dict[str, str]:
    metadata = {}
    match = re.search(r'<!--(.*?)-->', content, re.DOTALL)
    if match:
        metadata_block = match.group(1).strip()
        for line in metadata_block.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
    return metadata

def read_event_data() -> dict:
    event_path = os.getenv('GITHUB_EVENT_PATH')
    with open(event_path, 'r') as f:
        return json.load(f)

def post_to_medium(user_id: str, post_data: dict[str, str | list[str] | bool]) -> None:
    response = requests.post(f'{base_url}/users/{user_id}/posts', headers=headers, json=post_data)

def main() -> None:
    user_id = get_user_id()
    event_data = read_event_data()

    for commit in event_data['commits']:
        for file_path in commit['added'] + commit['modified']:
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
