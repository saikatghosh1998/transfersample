from github import Github
import base64

#  pip install PyGithub

# Authenticate with GitHub
g = Github("")

# Repository details
repo_name = "saikatghosh1998/transfersample"  # Replace with your repository details
repo = g.get_repo(repo_name)

# File details
file_path = ".github/CODEOWNERS"  # Standard location
branch = "main"

# List of reviewer IDs (GitHub usernames or team names prefixed with "@")
reviewers = ["@reviewer11", "@reviewer12", "@team-name"]  # Add all reviewers here

# Generate CODEOWNERS content for default reviewers
# Applying all reviewers to the root path `/` makes them default for all changes
codeowners_content = f"* {' '.join(reviewers)}"

try:
    # Check if the CODEOWNERS file exists
    file = repo.get_contents(file_path, ref=branch)
    # Update the existing CODEOWNERS file
    repo.update_file(
        file.path,
        "Update CODEOWNERS with default reviewers",
        codeowners_content,
        file.sha,
        branch=branch,
    )
    print("CODEOWNERS file updated successfully.")
except Exception as e:
    # Create a new CODEOWNERS file if it doesn't exist
    repo.create_file(
        file_path,
        "Create CODEOWNERS with default reviewers",
        codeowners_content,
        branch=branch,
    )
    print("CODEOWNERS file created successfully.")
