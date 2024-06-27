import os
import json
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
        modified_files.extend(commit.get('added', []))
        modified_files.extend(commit.get('modified', []))

    # デバッグ用に取得したファイルリストをログ出力
    logging.info(f"Modified files: {modified_files}")

    md_files = [f for f in modified_files if f.startswith('articles/') and f.endswith('.md')]

    if md_files:
        logging.info(f"Markdown files changed or added: {md_files}")
        print(f"::set-output name=has_md_files::true")
        print(f"::set-output name=md_files::{','.join(md_files)}")
    else:
        logging.info("No Markdown files were changed or added.")
        print(f"::set-output name=has_md_files::false")

if __name__ == "__main__":
    main()
