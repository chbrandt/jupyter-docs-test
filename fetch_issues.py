import requests

def fetch_issues(repo):
    issues = []
    url = f"https://api.github.com/repos/{repo}/issues?labels=documentation"
    response = requests.get(url)
    if response.status_code == 200:
        for issue in response.json():
            issues.append({
                'id': issue['id'],
                'title': issue['title'],
                'url': issue['html_url']
            })
    return issues

def main():
    repos = ["jupyterlab/jupyterlab", "jupyterlab/jupyterlab-desktop", "jupyter/notebook", "jupyterhub/jupyterhub"]
    all_issues = []
    for repo in repos:
        all_issues.extend(fetch_issues(repo))

    with open('jupyter_docs_issues.csv', 'w') as file:
        file.write('ID,Title,URL\n')
        for issue in all_issues:
            file.write(f"{issue['id']},{issue['title']},{issue['url']}\n")

if __name__ == "__main__":
    main()
