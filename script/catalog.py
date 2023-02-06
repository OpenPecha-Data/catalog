from github import Github
import requests
import os
import csv
import re



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


def get_repos_in_catalog(catalog):
    repos_in_catalog = set()  
    
    data = catalog.content.decode('utf-8')
    pechas_list = data.split("\n")
    pechas = list(csv.reader(pechas_list, delimiter=","))
    for pecha in pechas[1:-3]:
        pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
        if (pecha_id in repos_in_catalog):
            print(f"Pecha is already in catalog {pecha_id}")
        else:
            repos_in_catalog.add(pecha_id)
    return repos_in_catalog


def get_existing_pecha(repo):
    pass

if __name__ == "__main__":
    token = os.environ.get('GitHubToken')
    g = Github(token)
    repo = g.get_repo("OpenPecha-Data/catalog")
    catalog_csv = download_csv(repo)
    repos_in_catalog_set = get_repos_in_catalog(catalog_csv)
    existing_pecha_set = get_existing_pecha(repo)
    # save(catalog_csv,"catalog.txt")
