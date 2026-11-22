---
name: git-commit
description: Automate creating a git commit by analyzing `git status` and detailed diffs, clustering changes thematically, and generating a descriptive commit message. Prompts user for confirmation if needed.
license: Apache-2.0
compatibility: Requires git CLI.
tags: [git, workflow]
author: akatzmann (https://github.com/akatzmann)
version: "1.1.0"
---
# Git Commit: Atomic & PII-Gated Commits (`git-commit`)

> **Six-Pillar Agentic Engineering Suite**  
> Authored by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)


## Overview
Automates the process of creating a git commit:
1. Determines which files have changes via `git status --porcelain`.
2. Retrieves detailed diffs for each changed file via 'git diff'.
3. Analyzes diffs to group changes by file, folder or logical topic.
4. Generates a concise, human‑readable commit message summarizing the grouped changes.
5. If the user has specified a subset of files to commit, only those are included.
6. Prompts the user for confirmation when ambiguity exists (e.g., large number of files, unclear grouping, or custom message needed).
7. Executes `git add` for the selected files and creates the commit using the detailed, multi-line commit message.

## Input Parameters
- **files** *(optional)*: List of file paths to include in the commit. If omitted, all changes are considered.
- **message** *(optional)*: Custom commit message. If omitted, the skill generates one automatically.
- **autoConfirm** *(optional, default: true)*: When true, skips user confirmation and proceeds with the generated commit.
- **workdir** *(optional)*: Target git repository or git worktree directory (e.g., `.worktrees/<bead-id>-<slug>`). When specified, prefix all `git` commands with `git -C "<workdir>"` so commits happen strictly inside that worktree.

## Steps
1. **Gather Git Status**
   ```bash
   git status --porcelain
   ```
   Parse the output to obtain a list of changed files with status codes (M, A, D, etc.).
2. **Filter Files (if `files` provided)**
   - If the user supplied a specific list, intersect it with the status list.
   - If any supplied file is not present in the status, warn the user and ask for confirmation.
3. **Compute Diffs**
   For each selected file, run:
   ```bash
   git diff --unified=0 -- <file>
   ```
   Capture the diff output for analysis.
   
   If no files have been filtered, simply run git diff.
   and take note of the output.
4. **Ensure no absolute paths, secrets, or PII data**
   - Carefully make sure that the diff contains no absolute paths, secrets or PII data.
   - If the diff contains any such data, stop immediately and ask the user how to continue.
   - Provide useful options together with a recommendation on how to proceed, but also allow free text input.
5. **Cluster Changes**
   - Carefully read and understand the changes in the diff.
   - If the changes are complex or unclear, first, try reading the relevant codebase files to understand the changes.
   - If still unclear, ask the user for clarification.
   - Group changes by related functionality or area (e.g. Authentication, Database, API, UI, Tests).
6. **Generate Commit Message**
   - If a `message` is supplied, use it verbatim.
   - Otherwise, construct a multi‑line message:
     - **Title line** (preferably ≤50 chars) summarizing the main theme, and always introduced by [AI] (e.g., "[AI] feat: add button component and tests"). If the changes are complex, an adequate summary is used. (e.g., "[AI] complex: implementation of new caching strategy for database queries and modifications to API endpoints for supporting the new caching strategy")
     - **Body** IF only a few files where changed, listing grouped changes:
       ```
       * ui:
         - src/components/button.js
          - Added new button component with styling 
           - Fixed TODO in line 539 and 540 in the button component
         - src/styles/button.css
           - Added new button component styles
       * tests:
         - tests/button.test.js
           - Added new button component tests
       ```
     - **Body** IF many files where changed, group changes by feature, fix, or value created:
       ```
       * Added AI assistant in user management:
         - Touched src/components/button.js and tests/button.test.js
         - Added AI endpoint in src/backend/api
         - Adjusted src/backend/handlers for AI functionality
         - Updated database schemas to support AI features
       * Solved memory leak in user management:
         - ...
       ```
   - Ensure the message follows conventional‑commit style if possible.
   - **Optional `Verified:` Body Trailer:** Below the `[AI]` header and change summary body, you may append a lightweight trailer recording the verification scope actually executed:
     ```text
     Verified: <e2e+unit | unit | none>
     ```
     - Use `e2e+unit` when both end-to-end/repo-local verify checks and unit tests passed, `unit` when unit/targeted tests passed, or `none` for docs/metadata-only commits where no executable suite applies (omit if untracked).
     - Keep the trailer strictly limited to that status token — Step 4's absolute-path, secret, and PII gates apply equally to the commit title, body, and `Verified:` trailer.
     - Example with trailer:
       ```text
       [AI] feat(auth): validate token expiry before refresh [bd-123.1]

       * auth:
         - src/auth.py: reject expired refresh tokens
       * tests:
         - tests/test_auth.py: add expiry boundary test

       Verified: unit
       ```
7. **User Confirmation**
   - If `autoConfirm` is false or the commit message or file list is unclear, present the generated message and the list of files to be committed.
   - Ask: "Proceed with this commit? (yes/no)".
   - If the user replies "no", abort and optionally allow editing the message or file list.
   - You may present the users multiple options to choose from, for example:
     - Only commit feature X
     - Commit both feature X and fix Y
     - Commit all changes
     - Modify commit message
     - Abort the commit
8. **Stage Files & Enforce POSIX EOF Newline**
   - Ensure all newly created or edited text files end with a POSIX trailing newline (`\n`). Files lacking an EOF newline trigger IDE auto-formatters (e.g. `files.insertFinalNewline`), leaving dirty working trees immediately after commit.
   ```bash
   git add <file1> <file2> ...
   ```
9. **Create Commit (with Author Attribution & Worktree/Nested-Repo Selection)**
   - When committing changes inside a git worktree or nested repository (e.g., via `workdir`), run `git -C <workdir>` against that target repository.
   - Preserve author attribution (`GIT_AUTHOR_NAME` / `GIT_AUTHOR_EMAIL` or `--author="$GIT_AUTHOR_NAME <$GIT_AUTHOR_EMAIL>"`) whenever set in the environment.
   - Use a multi-line commit by piping the message to `git commit`:
   ```bash
   git commit -F- <<EOF
   <generated-message>
   EOF
   ```
10. **Verify Clean Working Tree & Report Result**
    - Output the new commit SHA.
    - Show a brief summary of what was committed.
    - Run `git status --porcelain` to verify the repository is clean. If an IDE auto-formatter or linter touched files with trailing newlines or whitespace immediately, stage and amend/commit so no pending changes remain.

## Guardrails
- Never run destructive commands (e.g., `git reset --hard`) without explicit user approval.
- If the number of changed files exceeds 20, require explicit confirmation regardless of `autoConfirm`.
- Validate that the generated commit message is non‑empty before committing.
- Preserve existing line endings and file permissions when staging.

## Usage Example
```bash
# Commit all changes with automatically generated message
git-commit

# Commit only specific files with a custom message
git-commit --files src/main.js docs/readme.md --message "fix: correct typo in README"

# Derive the arguments yourself (implies auto-confirm=false)
git-commit Commit all changes related to the new caching strategy
```

**Note**: This skill is designed to be invoked from the command line or as part of a larger automation pipeline.
