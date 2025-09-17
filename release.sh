#!/bin/bash
set -e

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <release-version> <next-snapshot-version>  # without \"v\" in front of version string"
  echo "Example: $0 1.0.0 1.0.1-SNAPSHOT"
  echo "Current version is $(grep '__version__' similarity_api_impl/version.py | cut -d '"' -f 2)"
  exit 1
fi

RELEASE_VERSION="$1"
NEXT_SNAPSHOT_VERSION="$2"
DATE=$(date +%Y-%m-%d)

# 1. set version in dev and commit
git checkout dev
echo "__version__ = \"$RELEASE_VERSION\"" > similarity_api_impl/version.py
git add similarity_api_impl/version.py
#set version and date in CITATION.cff
sed -i "s/^version: .*/version: \"$RELEASE_VERSION\"/" CITATION.cff
sed -i "s/^date-released: .*/date-released: \"${DATE}\"/" CITATION.cff
git add CITATION.cff
git commit -m "Release version $RELEASE_VERSION"
git push origin dev

# 2. merge to main
git checkout main
git merge dev
git push origin main

# 3. tag release and publish
git tag -a "v$RELEASE_VERSION" -m "Release version $RELEASE_VERSION"
git push origin "v$RELEASE_VERSION"
gh release create "v$RELEASE_VERSION" --title "Release $RELEASE_VERSION" --notes "Release $RELEASE_VERSION"

# 4. go back to dev and set next SNAPSHOT version
git checkout dev
echo "__version__ = \"$NEXT_SNAPSHOT_VERSION\"" > similarity_api_impl/version.py
git add similarity_api_impl/version.py
git commit -m "Prepare for next development iteration: $NEXT_SNAPSHOT_VERSION"
git push origin dev