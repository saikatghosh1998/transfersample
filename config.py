# config.py
config = {
    "BITBUCKET_WORKSPACE": "your_bitbucket_workspace",
    "BITBUCKET_REPO_SLUG": "your_bitbucket_repo_slug",
    "BITBUCKET_USERNAME": "your_bitbucket_username",
    "BITBUCKET_APP_PASSWORD": "your_bitbucket_app_password",
    "GITHUB_ORG": "your_github_org",
    "GITHUB_REPO": "your_github_repo",
    "GITHUB_TOKEN": "your_github_token"
}
#-------------------------------------------
# script1.py
from config import config

BITBUCKET_WORKSPACE = config["BITBUCKET_WORKSPACE"]
BITBUCKET_REPO_SLUG = config["BITBUCKET_REPO_SLUG"]
GITHUB_ORG = config["GITHUB_ORG"]
GITHUB_REPO = config["GITHUB_REPO"]
GITHUB_TOKEN = config["GITHUB_TOKEN"]

print(BITBUCKET_WORKSPACE, GITHUB_ORG)
