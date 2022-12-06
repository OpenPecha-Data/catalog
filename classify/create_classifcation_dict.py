import re
import requests
import yaml
import os
import shutil
import csv
from pathlib import Path
from git import Repo
from github import Github
from openpecha.utils import load_yaml, dump_yaml


config = {
    "OP_ORG": "https://github.com/Openpecha-Data"
    }

def clean_dir(path):
    if path.is_dir():
            shutil.rmtree(str(path))
            
            
def get_branch(repo, branch):
    if branch in repo.heads:
        return branch
    return "master"


def download_repo(repo_name, out_path=None, branch="master"):
    pecha_url = f"{config['OP_ORG']}/{repo_name}.git"
    out_path = Path(out_path)
    out_path.mkdir(exist_ok=True, parents=True)
    repo_path = out_path / repo_name
    Repo.clone_from(pecha_url, str(repo_path))
    repo = Repo(str(repo_path))
    branch_to_pull = get_branch(repo, branch)
    repo.git.checkout(branch_to_pull)
    return repo_path  

            
def get_metadata(g, pecha_id):
    metadata = {}
    if pecha_id[0] == "P" and len(pecha_id) == 7:
        repo = g.get_repo(f"Openpecha-Data/{pecha_id}")
        contents = repo.get_contents(f"{pecha_id}.opf/meta.yml")
        meta_content = contents.decoded_content.decode()
        metadata = yaml.safe_load(meta_content)
    else:
        file_path = Path(f"./pechas")
        repo_path = download_repo(pecha_id, file_path)
        meta_path = Path(f"{repo_path}/{repo_path.stem}.opf/meta.yml")
        metadata = load_yaml(meta_path)
    clean_dir(repo_path)
    return metadata


def get_pecha_dict(batch_path, g):
    pecha_list = batch_path.read_text(encoding='utf-8')
    for pecha_id in pecha_list:
        metadata = get_metadata(g, pecha_id)
        source_metadata = metadata["source_metadata"]
        initial_creation_type = metadata['initial_creation_type']
        if initial_creation_type == "ocr":
            id = source_metadata['id']
            title = source_metadata["title"]
        elif initial_creation_type == "ebook":
            id = source_metadata[""]
            title = source_metadata["title"]
    


if __name__ == '__main__':
    token = ""
    g = Github(token)
    batch_list = Path(f"./classify/csv_files/")
    for batch_file in list(os.listdir(batch_list)):
        batch_path = Path(f"{batch_list}/{batch_file}")
        pecha_dict = get_pecha_dict(batch_path)
        pecha_dict_path = Path(f"./classify/pecha_dicts/{batch_file[:-4]}.yml")
        dump_yaml(pecha_dict, pecha_dict_path)
    