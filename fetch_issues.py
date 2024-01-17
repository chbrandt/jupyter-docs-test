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


FIELDNAMES = ['repo', 'number', 'title', 'url']

# CSV reader/writer arguments for our 'issues' file
_CSV_ARGS = dict(
    fieldnames = FIELDNAMES,
    quoting = csv.QUOTE_NONNUMERIC,
)


def read_issues(filename):
    """
    Read issues from CSV 'filename'
    """
    issues = {}
    with open(filename) as file:
        reader = csv.DictReader(file, **_CSV_ARGS)
        # Escape the first/header line
        next(reader)
        for issue in reader:
            repo = issue.pop('repo')
            number = issue.pop('number')
            key = f"{repo}:{number}"
            issues[key] = issue
    return issues


def write_issues(issues, filename, write_md=False):
    """
    Write 'issues' to CSV 'filename'. Right a Markdown copy if 'write_md' True.
    """
    def _write_csv(issues, filename):
        with open(filename, 'w') as file:
            writer = csv.DictWriter(file, **_CSV_ARGS)
            # Write header line (ie, fieldnames)
            writer.writeheader()
            for key,issue in issues.items():
                repo, number = key.split(':')
                issue.update({'repo':repo, 'number':number})
                writer.writerow(issue)

    def _write_md(issues, filename):
        filename = '.'.join(filename.split('.')[:-1]) + '.md'
        with open(filename, 'w') as file:
            file.write(f"|{'|'.join(FIELDNAMES)}|\n")
            file.write(f"|{'|'.join(['===']*len(FIELDNAMES))}|\n")
            for key,issue in issues.items():
                repo, number = key.split(':')
                issue.update({'repo':repo, 'number':number})
                file.write(f"|{'|'.join(issue[key] for key in FIELDNAMES)}|\n")

    _write_csv(issues, filename)
    if write_md:
        _write_md(issues, filename)


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


def main(repos_file, issues_file, write_md):
    """
    Write CSV file from 'documentation' issues from 'repos_source.txt' file

    Github repositories listed in 'repos.list' file are queried for issues
    with label 'documentation' associated. Title, URL, and issue's number
    are collected and written in 'issues.csv'.
    """
    # List of (Github) repositories to query
    # repos_file = 'repos.list'
    # Issues' label (applied to all repos)
    label = 'documentation'
    # Retrieved issues table
    # issues_file = 'issues.csv'

    # Read list of repositories
    repos = read_list(repos_file)
    # print("Repos:", repos)

    # Read "old-current" list of issues
    try:
        current_issues = read_issues(issues_file)
        # print("Current issues:", current_issues.keys())
    except FileNotFoundError as err:
        current_issues = None
        # print("No previous issues to read.")

    ## Query repos for issues with 'label'
    issues = {}
    for repo in repos:
        issues.update(
            fetch_issues(repo, label=label)
            )

    # print("Queried issues:", issues.keys())
    # if current_issues:
    #     print("Diff:", set(issues).symmetric_difference(current_issues))

    ## Merge old/new list of issues
    all_issues = current_issues.copy() if current_issues else {}
    all_issues.update(issues)

    ## Write "new-current" list of issues
    write_issues(all_issues, issues_file, write_md)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos-file", default="repos.list",
                        help="Filename with list of Jupyter repos")
    parser.add_argument("--issues-file", default="issues.csv",
                        help="Filename for issues table (CSV)")
    parser.add_argument("--write-md", action="store_true",
                        help="Write a Markdown file (copy) of issues table")
    args = parser.parse_args()

    main(
        repos_file=args.repos_file,
        issues_file=args.issues_file,
        write_md=args.write_md
        )
