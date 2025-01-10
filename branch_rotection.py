def extract_branch_names_from_bitbucket_response(bitbucket_response):
    branch_names = []

    for restriction in bitbucket_response.get("values", []):
        branch_type = restriction.get("branch_type")
        if branch_type and branch_type not in branch_names:
            branch_names.append(branch_type)

    return branch_names
