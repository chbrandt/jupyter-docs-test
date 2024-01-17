import csv
import requests


def fetch_issues(repo, label='documentation'):
    """
    Query Github repos for issues with 'label'
    """
    url = f"https://api.github.com/repos/{repo}/issues?labels={label}"
    response = requests.get(url)
    issues = {}
    if response.status_code == 200:
        for issue in response.json():
            key = f"{repo}:{issue['number']}"
            issues[key] = {
                'title': issue['title'],
                'url': issue['html_url']
            }
    return issues


def read_list(filename):
    """
    Return list of lines in 'filename'.

    Example 'filename':
    $ cat > filename.txt << EOF
    jupyterlab/jupyterlab
    jupyterlab/jupyterlab-desktop
    jupyter/notebook
    jupyterhub/jupyterhub
    EOF
    """
    with open(filename) as file:
        lines = file.readlines()
    lines = [ line.strip() for line in lines ]
    lines = [ line for line in lines if line and line[0] != '#' ]
    return lines


def write_table(all_issues, filename):
    table = []
    fieldnames = ['repo', 'number', 'title', 'url']
    with open(filename, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for key,issue in all_issues.items():
            repo, number = key.split(':')
            issue.update({'repo':repo, 'number':number})
            writer.writerow(issue)

def main():
    """
    Write CSV file from 'documentation' issues from 'repos_source.txt' file

    Github repositories listed in 'repos_source.txt' file are queried for issues
    with label 'documentation' associated. Title, URL, and issue's number
    are collected and written in 'jupyter_docs_issues.csv'.
    """
    # List of (Github) repositories to query
    repos_file = 'repos_source.txt'
    # Issues' label (applied to all repos)
    label = 'documentation'
    # Retrieved issues table
    issues_file = 'jupyter_docs_issues.csv'

    repos = read_list(repos_file)

    all_issues = {}
    for repo in repos:
        all_issues.update(
            fetch_issues(repo, label=label)
            )

    write_table(all_issues, issues_file)

if __name__ == "__main__":
    main()
