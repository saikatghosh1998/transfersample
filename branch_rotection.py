def map_to_github_branch_rules(bitbucket_rules):
    github_rules = {}

    for rule in bitbucket_rules:
        branch_name = rule["matcher"]["id"]  # Get the branch or pattern
        if branch_name not in github_rules:
            github_rules[branch_name] = {
                "required_status_checks": None,  # GitHub-specific, leave as None unless specified
                "enforce_admins": True,
                "required_pull_request_reviews": {
                    "dismiss_stale_reviews": False,
                    "require_code_owner_reviews": False,
                    "required_approving_review_count": 1,  # Default to 1 approval
                },
                "restrictions": None,  # Restrict users/teams if needed
                "allow_force_pushes": False,
                "allow_deletions": True,  # Allow deletions unless overridden by a rule
                "require_signed_commits": False,
            }

        # Map Bitbucket rule types
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
