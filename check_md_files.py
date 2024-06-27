import os
import json
import requests
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    github_event_path = os.getenv('GITHUB_EVENT_PATH')
    if not github_event_path:
        logging.error("GITHUB_EVENT_PATH is not set.")
        exit(1)

    with open(github_event_path, 'r') as f:
        event_data = json.load(f)

    # デバッグ用にイベントデータをログ出力
    logging.info(f"Event data: {json.dumps(event_data, indent=2)}")

    modified_files = []
    for commit in event_data.get('commits', []):
        commit_id = commit['id']
        url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/commits/{commit_id}"
        headers = {'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commit_data = response.json()
        for file in commit_data.get('files', []):
            if file['filename'].startswith('articles/') and file['filename'].endswith('.md'):
                modified_files.append(file['filename'])

    logging.info(f"Modified files: {modified_files}")

    if modified_files:
        with open(os.getenv('GITHUB_ENV'), 'a') as env_file:
            env_file.write(f"has_md_files=true\n")
            env_file.write(f"md_files={','.join(modified_files)}\n")
    else:
        logging.info("No Markdown files were changed or added.")
        with open(os.getenv('GITHUB_ENV'), 'a') as env_file:
            env_file.write(f"has_md_files=false\n")

if __name__ == "__main__":
    main()
