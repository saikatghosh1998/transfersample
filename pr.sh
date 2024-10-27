
curl -u  $BITBUCKET_USERNAME:$BITBUCKET_APP_PASSWORD https://dev.code.saikat.com/rest/api/1.0/projects/asx/repos/$GITHUB_REPO/pull-requests > bitbucket_pr_response.json

# # Loop over each PR and extract data using jq
 jq -c '.values[]' bitbucket_pr_response.json | while read -r pr; do
#   # Extract the PR ID from the Bitbucket PR (this is needed to get the comments)
   PR_ID=$(echo $pr | jq -r '.id')
   PR_TITLE=$(echo $pr | jq -r '.title')
   PR_BODY=$(echo $pr | jq -r '.description')
   PR_BRANCH=$(echo $pr | jq -r '.fromRef.displayId')
   PR_BASE_BRANCH=$(echo $pr | jq -r '.toRef.displayId')
  
   echo "Creating PR: $PR_TITLE from $PR_BRANCH to $PR_BASE_BRANCH : PR ID is : $PR_ID"

   # Create the PR on GitHub
   json_payload=$(jq -n \
    --arg title "$PR_TITLE" \
    --arg body "$PR_BODY" \
    --arg head "$PR_BRANCH" \
    --arg base "$PR_BASE_BRANCH" \
    '{title: $title, body: $body, head: $head, base: $base}')

  echo "json $json_payload"

  response=$(curl -u $GITHUB_USERNAME:$GITHUB_PAT -X POST https://api.github.com/repos/$GITHUB_ORG/$GITHUB_REPO/pulls \
    -d "$json_payload" \
    -H "Accept: application/vnd.github.v3+json")
    
  echo $response > file.json

  # Extract the GitHub PR number from the response
  GITHUB_PR_NUMBER=$(echo $response | jq -r '.number')
  echo "This is Github PR number: $GITHUB_PR_NUMBER"

  if [ -z "$GITHUB_PR_NUMBER" ] || [ "$GITHUB_PR_NUMBER" == "null" ]; then
    echo "Failed to create PR on GitHub. Response: $response"
    continue
  fi

  echo "GitHub PR created with number: $GITHUB_PR_NUMBER"

#   # Get all comments for the current PR from Bitbucket using the PR_ID
  BITBUCKET_COMMENTS_URL="https://dev.sourcecode.kenvue.com/rest/api/latest/projects/asx-tgtp/repos/test1/pull-requests/$PR_ID/activities"
#   # Debug: Print the Bitbucket comments URL
   echo "Fetching comments from: $BITBUCKET_COMMENTS_URL"

  activities_response=$(curl --request GET \
    --user $BITBUCKET_USERNAME:$BITBUCKET_APP_PASSWORD \
    --header 'Accept: application/json' \
    --url "$BITBUCKET_COMMENTS_URL" \
    --no-progress-meter > bitbucket_comments_response.json)

#extracting comments
  jq -c '.values[]' bitbucket_comments_response.json | while read -r pr; do
    comment=$(echo $pr | jq -r '.comment.text')
    author=$(echo $pr | jq -r '.comment.author.name')
    comment_payload=$(jq -n --arg body "Comment by $author: $comment" '{body: $body}')

   #Pushing comments in github
  curl -u $GITHUB_USERNAME:$GITHUB_PAT -X POST https://api.github.com/repos/$GITHUB_ORG/$GITHUB_REPO/issues/$GITHUB_PR_NUMBER/comments \
    -d "$comment_payload" \
    -H "Accept: application/vnd.github.v3+json" 

done
done
