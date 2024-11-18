import requests

# Configuration
BITBUCKET_WORKSPACE = "your_bitbucket_workspace"
BITBUCKET_REPO_SLUG = "your_bitbucket_repo_slug"
BITBUCKET_USERNAME = "your_bitbucket_username"
BITBUCKET_APP_PASSWORD = "your_bitbucket_app_password"

GITHUB_ORG = "your_github_org"
GITHUB_REPO = "your_github_repo"
GITHUB_TOKEN = "your_github_token"

BITBUCKET_API_URL = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{BITBUCKET_REPO_SLUG}/pullrequests"
GITHUB_ISSUES_URL = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/issues"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# Fetch PR activity for approvals and merge details
def fetch_pr_activity(pr_id):
    activity_url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{BITBUCKET_REPO_SLUG}/pullrequests/{pr_id}/activity"
    response = requests.get(activity_url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
    approvals = []
    merged_by = None

    if response.status_code == 200:
        activities = response.json().get("values", [])
        print("Fetched Activity Data:")  # Debugging
        print(activities)  # Print the raw activity data to inspect the structure

        for activity in activities:
            if "approval" in activity:
                approvals.append({
                    "approver": activity["approval"]["user"]["display_name"],
                    "date": activity["approval"]["date"],
                })
            # Look for merge activity and debug its structure
            if activity.get("update", {}).get("state") == "MERGED":
                merged_by = activity.get("update", {}).get("author", {}).get("display_name", "Unknown")
    else:
        print(f"Failed to fetch PR activity: {response.status_code}, {response.text}")
    
    return approvals, merged_by
# Fetch PRs from Bitbucket
def fetch_bitbucket_prs(state="MERGED"):
    pr_list = []
    next_url = BITBUCKET_API_URL + f"?state={state}"
    
    while next_url:
        response = requests.get(next_url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
        if response.status_code == 200:
            data = response.json()
            pr_list.extend(data.get("values", []))
            next_url = data.get("next")  # Pagination
        else:
            print(f"Failed to fetch PRs from Bitbucket: {response.status_code}, {response.text}")
            break
    return pr_list

# Create a GitHub issue to simulate a PR
def create_github_issue(title, body, labels):
    payload = {
        "title": title,
        "body": body,
        "labels": labels,
    }
    response = requests.post(GITHUB_ISSUES_URL, json=payload, headers=HEADERS)
    if response.status_code == 201:
        print(f"Created issue for PR: {title}")
    else:
        print(f"Failed to create issue: {response.status_code}, {response.text}")

# Migrate PRs as issues
def migrate_prs_to_github():
    # Fetch merged PRs
    merged_prs = fetch_bitbucket_prs(state="MERGED")
    print(f"Fetched {len(merged_prs)} merged PRs.")

    for pr in merged_prs:
        title = f"[Migrated PR] {pr['title']}"
        author = pr["author"]["display_name"]
        created_on = pr["created_on"]
        body = pr.get("description", "No description provided.")
        destination_branch = pr["destination"]["branch"]["name"]
        source_branch = pr["source"]["branch"]["name"]

        # Add PR metadata to the issue body
        issue_body = (
            f"**Author:** {author}\n"
            f"**Created On:** {created_on}\n"
            f"**Source Branch:** {source_branch}\n"
            f"**Destination Branch:** {destination_branch}\n\n"
            f"{body}"
        )

        # Use labels to differentiate merged PRs
        create_github_issue(title, issue_body, labels=["migrated-PR", "merged-PR"])

if __name__ == "__main__":
    migrate_prs_to_github()
