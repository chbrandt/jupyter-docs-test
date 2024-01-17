import csv
import requests
from pprint import pprint

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


_CSV_ARGS = dict(
    fieldnames = ['repo', 'number', 'title', 'url'],
    quoting = csv.QUOTE_NONNUMERIC,
)


def read_issues(issues_file):
    issues = {}
    with open(issues_file) as file:
        reader = csv.DictReader(file, **_CSV_ARGS)
        # Escape the first/header line
        next(reader)
        for issue in reader:
            repo = issue.pop('repo')
            number = issue.pop('number')
            key = f"{repo}:{number}"
            issues[key] = issue
    return issues


def write_issues(issues, filename):
    with open(filename, 'w') as file:
        writer = csv.DictWriter(file, **_CSV_ARGS)
        # Write header line (ie, fieldnames)
        writer.writeheader()
        for key,issue in issues.items():
            repo, number = key.split(':')
            issue.update({'repo':repo, 'number':number})
            writer.writerow(issue)


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


def main():
    """
    Write CSV file from 'documentation' issues from 'repos_source.txt' file

    Github repositories listed in 'repos.list' file are queried for issues
    with label 'documentation' associated. Title, URL, and issue's number
    are collected and written in 'issues.csv'.
    """
    # List of (Github) repositories to query
    repos_file = 'repos.list'
    # Issues' label (applied to all repos)
    label = 'documentation'
    # Retrieved issues table
    issues_file = 'issues.csv'

    # Read list of repositories
    repos = read_list(repos_file)
    print("Repos:", repos)

    # Read current/pass list of issues
    try:
        current_issues = read_issues(issues_file)
        print("Current issues:")
        pprint(current_issues.keys())
    except FileNotFoundError as err:
        print("No previous issues to read.")
        current_issues = None

    issues = {}
    for repo in repos:
        issues.update(
            fetch_issues(repo, label=label)
            )
    print("Queried issues:")
    pprint(issues.keys())

    if current_issues:
        print("Diff:", set(issues).symmetric_difference(current_issues))

    all_issues = current_issues.copy() if current_issues else {}
    all_issues.update(issues)

    write_issues(all_issues, issues_file)


if __name__ == "__main__":
    main()
