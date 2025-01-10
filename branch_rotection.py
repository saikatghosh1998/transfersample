def map_to_github_branch_rules(bitbucket_rules):
    github_rules = {}

    for rule in bitbucket_rules:
        branch_name = rule["matcher"]["id"]  # Get the branch or pattern
        if branch_name not in github_rules:
            # Initialize default GitHub rules for the branch
            github_rules[branch_name] = {
                "required_status_checks": {  # Required field
                    "strict": False,        # Set to False by default
                    "contexts": []          # Empty list for no status checks
                },
                "enforce_admins": False,  # Set to False by default
                "required_pull_request_reviews": {  # Required field
                    "dismiss_stale_reviews": False,
                    "require_code_owner_reviews": False,
                    "required_approving_review_count": 0
                },
                "restrictions": None,  # Optional field, can be set to None if no restrictions
                "allow_force_pushes": False,  # Set to False by default
                "allow_deletions": True,  # Allow deletions unless overridden by a rule
                "require_signed_commits": False  # Optional, set to False
            }

        # Map Bitbucket rule types to GitHub rules
        if rule["type"] == "no-deletes":
            github_rules[branch_name]["allow_deletions"] = False

        if rule["type"] == "pull-request-only":
            github_rules[branch_name]["required_pull_request_reviews"]["required_approving_review_count"] = 1
            github_rules[branch_name]["restrictions"] = {
                "users": [],
                "teams": [],
                "apps": []
            }

    return github_rules



def apply_github_branch_rules(github_repo, branch, rules):
    url = f"{GITHUB_BASE_URL}/repos/{GITHUB_ORG}/{github_repo}/branches/{branch}/protection"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Adjust payload to match GitHub's API requirements
    payload = {
        "required_status_checks": rules["required_status_checks"],  # Cannot be None
        "enforce_admins": rules["enforce_admins"],
        "required_pull_request_reviews": rules["required_pull_request_reviews"],
        "restrictions": rules["restrictions"],  # Can be None
        "allow_force_pushes": rules["allow_force_pushes"],
        "allow_deletions": rules["allow_deletions"],
        "require_signed_commits": rules["require_signed_commits"]
    }

    # Send the request
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 200:
        logger.info(f"Successfully applied rules to branch '{branch}'")
        return True
    elif response.status_code == 404:
        logger.warning(f"Branch '{branch}' not found in GitHub, skipping.")
        return False
    else:
        logger.error(f"Failed to apply rules to branch '{branch}': {response.status_code} - {response.text}")
        return False

