#!/usr/local/bin/bash

# Example implementation

# repo and source branch from which to create your fork and open a PR against
UPSTREAM_OWNER="upstream_owner"
UPSTREAM_BRANCH="master"

# repo and destination branch that will be created in order to open the PR
DOWNSTREAM_OWNER="downstream_owner"
DOWNSTREAM_BRANCH="foo"

COMMIT_MSG="my super cool commit"
PR_MSG="my super cooll PR"

update () {
PROJECT=$1

# update Makefile
cat > "$PROJECT/somefile" <<"EOF"

some content

EOF

git add .
git commit -m "$COMMIT_MSG"
git push --set-upstream origin "$DOWNSTREAM_BRANCH"

hub pull-request\
 --base "$UPSTREAM_OWNER:$UPSTREAM_BRANCH"\
 --head "$DOWNSTREAM_OWNER:$DOWNSTREAM_BRANCH"\
 --message "$PR_MSG"
} 


## Run update against all repos
dir_list=($(ls -d $(pwd)/tardigrade-ci/*))

for project in "${dir_list[@]}"; do
  (cd "$project" && update $project)
done