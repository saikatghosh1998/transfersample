import requests
from requests.auth import HTTPBasicAuth

# Replace these variables with your actual values
username = "your_username"
app_password = "your_app_password"
workspace = "your_workspace"
repo_slug = "your_repo_slug"

# Initial API URL to fetch branches
url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/refs/branches"

# Authentication
auth = HTTPBasicAuth(username, app_password)

# Loop to handle pagination and fetch all branches
while url:
    try:
        # Fetch the data with a timeout of 30 seconds
        response = requests.get(url, auth=auth, timeout=30)
        
        # Check the status code of the response
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            break  # Exit if there was an issue with the request
        
        data = response.json()

        # Loop through each branch in the current page
        for branch in data.get("values", []):
            # Extract required details from each branch
            branch_name = branch.get("name")
            is_default = branch.get("is_default", False)
            author_name = branch.get("target", {}).get("author", {}).get("display_name", "Unknown")

            # Print the details
            print(f"Branch Name: {branch_name}")
            print(f"Is Default: {is_default}")
            print(f"Author: {author_name}")
            print("-" * 40)
        
        # Move to the next page if available
        url = data.get("next")
        if not url:
            print("No more pages available. Ending script.")
            break  # Exit if there are no more pages

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        break
