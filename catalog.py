from github import Github
import requests
import os
import csv
import re
import yaml
from pathlib import Path


def download_csv(repo):
    """From the GitHub repository, it will download specific file

    Args:
        repo (repo): An object of repository to get access to the content of a file

    Returns:
        catalog_csv: Get the content of the file in a http reponse format. 
    """
    file = repo.get_contents("data/catalog.csv", ref="master")
    catalog_csv = requests.get(file.download_url, stream=True)
    return catalog_csv


def get_repos_in_catalog(data):
    """All the pecha ids that was there in the catalog file are parsed into a variable

    Args:
        catalog (http_response): Got the downloaded catalog.csv file in http response format

    Returns:
        set: Get all repos pecha_ids in catalog.csv file been parsed and returned
    """
    repos_in_catalog = list()

    pechas_list = data.split("\n")
    pechas = list(csv.reader(pechas_list, delimiter=","))

    # Use enumerate to get the index of each row
    for index, pecha in enumerate(pechas[1:-3]):
        pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
        if pecha_id in repos_in_catalog:
            print(f"Pecha {pecha_id} is already in catalog in row {index+2}")
        else:
            repos_in_catalog.append(pecha_id)
    return repos_in_catalog


def get_repo_names(repos, repos_in_catalog_set):
    """Fetching the data and update the row into the catalog.csv file. 
    Args:
        repo (repo): An object of repository to get access to the metadata of the each repo in the list 
        repos_in_catalog_set(set) : repos which are in the catalog
    Returns:
        catalog_csv: Get the content of the file in a http reponse format. 
    """
    repo_names = list()
    excluded_repo_names = ["catalog", "users", "ebook-template", "alignments", "openpecha-template", "collections",
                           "data-translation-memory", "openpecha-toolkit", "openpecha.github.io", "Transifex-Glossary",
                           "W00000003", "works", "works-bak", ".github", "Openpecha_Action", "pecha-collection-repo-template"]

    for repo in repos:
        repo_name = repo.name

        if len(repo_name) >= 9 or repo_name[0] == 'A':
            excluded_repo_names.append(repo_name)

        if repo_name in excluded_repo_names:
            continue
        else:
            if repo_name in repos_in_catalog_set:
                continue
            else:
                repo_names.append(repo_name)

    return repo_names


def add_new_rows_to_catalog(g, repo_lists):
    """Fetching the data and update the row into the catalog.csv file. 
    Args:
        g (github) : It is a github API opened with github token. 
        repo (repo): An object of repository to get access to the metadata of the each repo in the list 
        
    Returns:
        catalog_csv: Get the content of the file in a http reponse format. 
    """
    for repo in repo_lists:
        pecha_id = repo
        row = ""

        if pecha_id[0] == "I" or pecha_id[0] == "P":
            try:
                repo = g.get_repo(f"OpenPecha-Data/{pecha_id}")
                contents = repo.get_contents(f"{pecha_id}.opf/meta.yml")
                meta_content = contents.decoded_content.decode()
                metadata = yaml.safe_load(meta_content)
                source_metadata = metadata['source_metadata']
                work_id = source_metadata.get('id', "")
                title = source_metadata.get('title', "")

                if title == '':
                    if work_id == '':
                        row = f"[{pecha_id}](https://github.com/Openpecha-Data/{pecha_id}),,,,\n"
                    else:
                        row = f"[{pecha_id}](https://github.com/Openpecha-Data/{pecha_id}),,,,{work_id}\n"
                else:
                    if work_id != None:
                        row = f"[{pecha_id}](https://github.com/Openpecha-Data/{pecha_id}),{title},,,{work_id}\n"
                    else:
                        row = f"[{pecha_id}](https://github.com/Openpecha-Data/{pecha_id}),{title},,,\n"

                    with open(f"./data/catalog.csv", "a", encoding='utf-8') as csvfile:
                        csvfile.write(row)
            except Exception as e:
                print(f"An exception occured {e}")


def upload_changed_catalog(repo):
    new_content = Path("./data/catalog.csv").read_text(encoding='utf-8')
    try:
        git_file = "data/catalog.csv"
        content = repo.get_contents(git_file, ref="master")
        repo.update_file(content.path, "Weekly catalog Update",
                         new_content, content.sha, branch="master")
    except Exception as e:
        print("Catalog repo not found")


if __name__ == "__main__":
    token = os.environ.get('SECRET')
    g = Github(token)
    repo = g.get_repo("OpenPecha-Data/catalog")
    catalog_csv = download_csv(repo)
    data = catalog_csv.content.decode('utf-8')
    repos_in_catalog_set = get_repos_in_catalog(data)
    repos = g.get_user("OpenPecha-Data").get_repos()
    repo_names = get_repo_names(repos, repos_in_catalog_set)
    add_new_rows_to_catalog(g, repo_names)
    upload_changed_catalog(repo)
