import os
import subprocess
import requests

# Define variables
BITBUCKET_USERNAME = "your_bitbucket_username"
BITBUCKET_APP_PASSWORD = "your_bitbucket_app_password"
BITBUCKET_SERVER_URL = "https://your_bitbucket_server_url"
GITHUB_ORG = "your_github_organization"
GITHUB_TOKEN = "your_github_token"
CHECKPOINT_FILE = "migrated_repos.txt"

# Function to load migrated repositories from the checkpoint file
def load_migrated_repos():
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE, "r") as file:
        return {line.strip() for line in file}

# Function to save a migrated repository to the checkpoint file
def save_migrated_repo(repo_name):
    with open(CHECKPOINT_FILE, "a") as file:
        file.write(f"{repo_name}\n")

# Function to migrate a repository
def migrate_repo(repo_name):
    # Skip if already migrated
    if repo_name in migrated_repos:
        print(f"Repository '{repo_name}' has already been migrated. Skipping...")
        return
    
    # Construct the Bitbucket repository URL
    bitbucket_repo_auth = f"https://{BITBUCKET_USERNAME}:{BITBUCKET_APP_PASSWORD}@{BITBUCKET_SERVER_URL.split('//')[1]}/scm/project_key/{repo_name}.git"
    
    print(f"Cloning Bitbucket repository: {bitbucket_repo_auth}")
    subprocess.run(["git", "clone", "--mirror", bitbucket_repo_auth], check=True)

    # Change directory to the cloned repository
    os.chdir(f"{repo_name}.git")

    # Create the GitHub repository
    github_repo_url = f"https://api.github.com/orgs/{GITHUB_ORG}/repos"
    print(f"Creating GitHub repository for: {repo_name}")
    
    response = requests.post(
        github_repo_url,
        json={"name": repo_name, "private": True},
        headers={"Authorization": f"token {GITHUB_TOKEN}"}
    )
    
    # Check if the repository was created successfully
    if response.status_code == 201:
        print(f"Successfully created GitHub repository for: {repo_name}")
    else:
        print(f"Failed to create GitHub repository for: {repo_name}. Response: {response.text}")
        os.chdir("..")
        subprocess.run(["rm", "-rf", f"{repo_name}.git"], check=True)
        return

    # Push all branches, commits, and tags to GitHub
    github_repo = f"https://github.com/{GITHUB_ORG}/{repo_name}.git"
    subprocess.run(["git", "remote", "add", "github", github_repo], check=True)
    
    print(f"Pushing to GitHub: {github_repo}")
    subprocess.run(["git", "push", "--mirror", "github"], check=True)

    # Check if the push was successful
    print(f"Successfully pushed repository: {repo_name}")

    # Save to checkpoint
    save_migrated_repo(repo_name)

    # Cleanup
    print(f"Deleting {repo_name}.git from local")
    os.chdir("..")
    subprocess.run(["rm", "-rf", f"{repo_name}.git"], check=True)

# Load migrated repositories
migrated_repos = load_migrated_repos()

# Check if the repository file exists
REPO_FILE = "repositories.txt"  # File containing the list of repositories to migrate
if not os.path.isfile(REPO_FILE):
    print(f"Repository file {REPO_FILE} not found.")
    exit(1)

print(f"Reading repositories from {REPO_FILE}...")
with open(REPO_FILE, "r") as file:
    for line in file:
        repo = line.strip()
        if not repo:
            print("Skipping empty line in REPO_FILE")
            continue
        print(f"Read repository: '{repo}'")
        migrate_repo(repo)

print("Finished reading repositories.")
