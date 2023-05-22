import csv
from github import Github
import os
import yaml
import time
import requests
from datetime import datetime
from github.GithubException import GithubException


def get_meta(repo_name, meta_path):
    branch = "master"
    token = os.getenv("SECRET")
    token = token.replace("\n","")
    g = Github(token)
    try:
        repo = g.get_repo(f"OpenPecha-Data/{repo_name}")
        file = repo.get_contents(meta_path, ref=branch)
        file_content = file.decoded_content.decode('utf-8')
        meta = yaml.safe_load(file_content)
        return meta
    except GithubException as e:
        if e.status == 403 and 'rate limit' in e.data.get('message', ''):
            rate_limit = g.get_rate_limit()
            reset_time = rate_limit.core.reset.timestamp()
            current_time = time.time()
            wait_time = reset_time - current_time
            if wait_time > 0:
                print(f"Rate limit exceeded. Waiting for {wait_time:.2f} seconds until reset.")
                time.sleep(wait_time)
                return get_meta(repo_name, meta_path)
            else:
                print("Rate limit exceeded. Please try again later.")
        else:
            print("A GitHub API error occurred:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None


def get_row(repo_name):
    row = []
    if repo_name.startswith(('A')):
        meta_path= f"{repo_name}.opa/meta.yml"
        meta = get_meta(repo_name,meta_path)
        if meta is None:
            return
        title = meta["title"] if "title" in meta.keys() else "----"
        row = [repo_name,title]
    elif repo_name.startswith(('P','I','O','D')):
        meta_path= f"{repo_name}.opf/meta.yml"
        meta = get_meta(repo_name,meta_path)
        if meta is None:
            return
        id = repo_name
        title = meta["title"] if "title" in meta.keys() else "----"
        volume = meta["volume"] if "volume" in meta.keys() else "----"
        author = meta["author"] if "author" in meta.keys() else "----"
        source_id = meta["soource_id"] if "source_id" in meta.keys() else "----"
        legacy_id = meta["legacy_id"] if "legacy_id" in meta.keys() else  "----"
        creation_date = meta["imported"] if "imported" in meta.keys() else "----"
        last_update = meta["last_modified"] if "last_modified" in meta.keys() else "----"
        row = [id,title,volume,author,source_id,legacy_id,creation_date,last_update]
    return row


def add_new_row_to_catalog(repos,catalog_path):
    with open(catalog_path, 'a', newline='') as file:
        writer = csv.writer(file)
        for repo in repos:
            row = get_row(repo)
            writer.writerow(row)
    

def get_org_repos(g):
    org_repos = []
    org_name = 'OpenPecha-Data'  # Replace with the name of the organization
    org = g.get_organization(org_name)  
    repos = org.get_repos()
    for repo in repos:
        org_repos.append(repo.name)
    return org_repos


def get_all_repos(org_name, token):
    repos = []
    page = 1
    per_page = 100  # Number of repositories to retrieve per page

    while True:
        # Make a request to the GitHub API to retrieve repositories for the organization
        url = f'https://api.github.com/orgs/{org_name}/repos?page={page}&per_page={per_page}'
        headers = {'Accept': 'application/vnd.github.v3+json', 'Authorization': f'token {token}'}
        response = requests.get(url, headers=headers)

        # Handle rate limit exceeded error
        if response.status_code == 403 and 'rate limit exceeded' in response.text:
            reset_time = datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))
            sleep_seconds = (reset_time - datetime.now()).total_seconds() + 10  # Add extra time buffer
            print(f'Rate limit exceeded. Sleeping for {sleep_seconds} seconds.')
            time.sleep(sleep_seconds)
            continue

        # Handle other errors
        if response.status_code != 200:
            print(f'Error occurred while fetching repositories: {response.status_code}')
            break

        # Retrieve repositories from the response
        repositories = response.json()

        # Add repositories to the list
        repos.extend([repo['name'] for repo in repositories])
        print(repos)
        print(f"Number of repos:{len(repos)}")

        # Check if there are more pages to retrieve
        if len(repositories) < per_page:
            break

        # Increment the page number for the next request
        page += 1

    return repos


def get_repos_in_catalog(catalog_path):
    repos_in_catalog = []
    with open(catalog_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            repos_in_catalog.append(row[0])
    return repos_in_catalog 


def get_new_repos(org_repos,opfs_in_catalog,opas_in_catalog):
    new_opfs = []
    new_opas = []
    for repo in org_repos:
        if repo in opfs_in_catalog or repo in opas_in_catalog:
            continue
        if repo.startswith(('P','I','O','D')):
            new_opfs.append(repo)
        elif repo.startswith(('A')):
            new_opas.append(repo)
    return new_opfs,new_opas


def main():
    opf_catalog_path = "opf_catalog.csv"
    opa_catalog_path = "opa_catalog.csv"
    token = os.environ.get('SECRET')
    token = token.replace("\n","")
    org_name = "OpenPecha-Data"
    opfs_in_catalog = get_repos_in_catalog(opf_catalog_path)
    opas_in_catalog = get_repos_in_catalog(opa_catalog_path)
    org_repos = get_all_repos(org_name,token)
    new_opfs,new_opas = get_new_repos(org_repos,opfs_in_catalog,opas_in_catalog)
    add_new_row_to_catalog(new_opfs,opf_catalog_path)
    add_new_row_to_catalog(new_opas,opa_catalog_path)


if __name__ == '__main__':
    main()
    