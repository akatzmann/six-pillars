---
name: git-release
description: Automate creating a GitHub release using the `gh` CLI. Supports custom versions or auto-suggesting the next semantic version, auto-generating release notes, and always prompts for user confirmation before submitting.
license: Apache-2.0
compatibility: Requires git CLI and GitHub CLI (gh) authenticated.
tags: [git, github, workflow, release]
author: akatzmann (https://github.com/akatzmann)
version: "1.0.0"
---
# Git Release: Automated Semantic Releases (`git-release`)

> **Six-Pillar Agentic Engineering Suite**  
> Authored by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)

## Overview

Automates the process of publishing a GitHub release for the repository using the `gh` command-line tool. It calculates the next release version (if not provided), automatically generates high-quality release notes from the commit logs, and strictly enforces user confirmation before publishing.

## Input Parameters
- **version** *(optional)*: The target version tag for the release (e.g., `v1.2.0`). If omitted, the skill automatically suggests the next patch version based on the latest tag.
- **title** *(optional)*: The title of the release. Defaults to the version tag if not specified.
- **notes** *(optional)*: Custom release notes markdown text. If omitted, the skill dynamically generates standard release notes using the GitHub API.
- **target** *(optional, default: current branch)*: The branch or commit SHA to release from.
- **draft** *(optional, default: false)*: Create the release as a draft.
- **prerelease** *(optional, default: false)*: Mark the release as a pre-release.

## Steps

1. **Verify Prerequisites**
   Verify the `gh` CLI is installed and authenticated:
   ```bash
   which gh
   gh auth status
   ```
   If not authenticated, guide the user to run `gh auth login`.

2. **Retrieve Latest Version Tag**
   Find the latest tag in the local repository:
   ```bash
   git fetch --tags
   git tag --sort=-v:refname | head -n 1
   ```
   *   If no tags are found, suggest starting with `v0.1.0` or `v1.0.0`.

3. **Determine Target Release Version**
   *   If a specific `version` input is provided by the user, validate that it uses standard semver naming (preferably starting with a `v` prefix).
   *   If no version is provided, automatically increment the latest tag to suggest a new version:
       *   **Default**: Increment the Patch version (e.g., `v1.2.3` -> `v1.2.4`).
       *   Provide options to increment Minor (`v1.3.0`) or Major (`v2.0.0`) instead.

4. **Generate Release Notes**
   *   If a custom `notes` argument is provided, use it.
   *   Otherwise, compile and analyze the commit logs since the last tag (or since the initial commit if no tags exist):
       ```bash
       # Get commits since the last release tag
       git log <last-tag>..HEAD --oneline
       ```
   *   Analyze these commits to write a **concise but comprehensive overview** of all changes. The release notes should cluster changes logically into categories, such as:
       - **🚀 Features & Improvements**
       - **🐛 Bug Fixes**
       - **📝 Documentation & Refactoring**
       - **🎨 Style & UI Tweaks**
   *   Alternatively, run `gh release generate-notes --tag <new-version> --target <target-branch>` to retrieve a draft, but refine and format it to ensure it contains a human-readable, structured overview of all changes rather than a simple raw dump of commit messages or pull requests.

5. **Mandatory User Confirmation**
   *   **IT IS CRITICAL THAT NO RELEASE IS SUBMITTED WITHOUT USER APPROVAL.**
   *   Present the proposed release details in the console:
       *   **Tag**: `<version>`
       *   **Branch/Commit**: `<target>`
       *   **Release Title**: `<title>`
       *   **Flags**: `[Draft]` / `[Pre-release]`
       *   **Release Notes Preview**: (First few lines or summary of generated notes)
   *   Prompt the user:
       `Confirm and publish this release? (yes/no/edit)`
   *   If the user chooses `no` or cancels, abort execution immediately without creating any tags or releases on GitHub.
   *   If the user chooses `edit`, allow them to supply different values for the tag, title, or notes before returning to confirmation.

6. **Create and Publish the Release**
   *   Execute the release creation command:
       ```bash
       gh release create <version> \
         --target <target> \
         --title "<title>" \
         --notes "<generated-or-custom-notes>" \
         ${draft:+"--draft"} \
         ${prerelease:+"--prerelease"}
       ```
   *   Output the URL of the newly created release.

## Guardrails
- **Never publish silently.** If running in a non-interactive automated pipeline, require a explicit force flag or fail execution if user confirmation is missing.
- Ensure the local repository is synchronized with origin (`git status` and `git diff` should be checked to make sure there are no unpushed commits on the target branch).
- Ensure the tag does not already exist on origin:
  ```bash
  git ls-remote --tags origin refs/tags/<version>
  ```

## Usage Examples

```bash
# Create a release, auto-suggesting the version and generating notes
git-release

# Create a specific version with a custom title
git-release --version v1.3.0 --title "v1.3.0: High Performance Routing"

# Create a draft pre-release
git-release --prerelease --draft
```
