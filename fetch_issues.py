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


# CSV/MD columns
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

    Return list of filename(s) created.
    """
    def _write_csv(issues, filename):
        """Write CSV file"""
        with open(filename, 'w') as file:
            writer = csv.DictWriter(file, **_CSV_ARGS)
            # Write header line (ie, fieldnames)
            writer.writeheader()
            for key,issue in issues.items():
                repo, number = key.split(':')
                issue.update({'repo':repo, 'number':number})
                writer.writerow(issue)
        return filename

    def _write_md(issues, filename):
        """Write Markdown table file"""
        filename = '.'.join(filename.split('.')[:-1]) + '.md'
        with open(filename, 'w') as file:
            file.write(f"|{'|'.join(FIELDNAMES)}|\n")
            file.write(f"|{'|'.join(['---']*len(FIELDNAMES))}|\n")
            for key,issue in issues.items():
                repo, number = key.split(':')
                issue.update({'repo':repo, 'number':number})
                file.write(f"|{'|'.join(issue[key] for key in FIELDNAMES)}|\n")
        return filename

    files_out = []
    files_out.append(_write_csv(issues, filename))
    if write_md:
        files_out.append(_write_md(issues, filename))

    return files_out


def read_repos(filename):
    """
    Return list of repositories in 'filename'.

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
    ## Issues' label (applied to all repos)
    label = 'documentation'

    ## Read list of repositories
    repos = read_repos(repos_file)

    # ## Read "old-current" list of issues
    # try:
    #     current_issues = read_issues(issues_file)
    # except FileNotFoundError as err:
    #     current_issues = None

    ## Ignore previous issues, we're not keeping track, we just want today's
    current_issues = None

    ## Query repos for issues with 'label'
    issues = {}
    for repo in repos:
        issues.update(
            fetch_issues(repo, label=label)
            )

    print(f"{len(issues)} issues found.")

    # if current_issues:
    #     print("Diff:", set(issues).symmetric_difference(current_issues))

    ## Merge old/new list of issues
    all_issues = current_issues.copy() if current_issues else {}
    all_issues.update(issues)

    ## Write "new-current" list of issues
    files_out = write_issues(all_issues, issues_file, write_md)
    print(f"Files created: {(', ').join(files_out)}.")


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
