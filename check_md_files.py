import os
import json

def main():
    github_event_path = os.getenv('GITHUB_EVENT_PATH')
    if not github_event_path:
        print("GITHUB_EVENT_PATH is not set.")
        exit(1)

    with open(github_event_path, 'r') as f:
        event_data = json.load(f)

    modified_files = []
    for commit in event_data.get('commits', []):
        modified_files.extend(commit.get('added', []))
        modified_files.extend(commit.get('modified', []))

    md_files = [f for f in modified_files if f.startswith('articles/') and f.endswith('.md')]

    if md_files:
        print(f"Markdown files changed or added: {md_files}")
        print(f"::set-output name=has_md_files::true")
        print(f"::set-output name=md_files::{','.join(md_files)}")
    else:
        print("No Markdown files were changed or added.")
        print(f"::set-output name=has_md_files::false")

if __name__ == "__main__":
    main()
