---
name: git-commit
description: Write well-structured git commit messages following Conventional Commits format. Use when the user asks to commit changes, write a commit message, or summarize staged changes.
license: Apache-2.0
---

# Git Commit

Write a clear, structured commit message following the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Steps

1. Run `git diff --staged` to review all staged changes.
2. Identify the primary change type and affected scope.
3. Write the commit message in the format below.
4. Run `git commit -m "<message>"` (or show the message for review if the user hasn't staged changes yet).

## Commit Message Format

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

### Types

| Type       | Use when...                                      |
|------------|--------------------------------------------------|
| `feat`     | Adding a new feature                             |
| `fix`      | Fixing a bug                                     |
| `docs`     | Documentation changes only                       |
| `style`    | Formatting, missing semicolons, etc. (no logic)  |
| `refactor` | Code restructuring without feature/bug change    |
| `test`     | Adding or updating tests                         |
| `chore`    | Build process, dependency updates, tooling       |
| `perf`     | Performance improvements                         |
| `ci`       | CI/CD configuration changes                      |

### Rules

- Summary line: max 72 characters, imperative mood ("add" not "added")
- Scope: optional, describes the affected module/component
- Body: explain *what* and *why*, not *how*; wrap at 72 characters
- Breaking changes: add `BREAKING CHANGE:` in the footer

## Examples

```
feat(auth): add OAuth2 login with GitHub

Implements GitHub OAuth2 flow so users can sign in without a password.
Stores the access token in an encrypted cookie.

Closes #42
```

```
fix(api): handle null response from payment gateway

The payment gateway occasionally returns null on timeout.
Previously this caused an unhandled exception; now returns a 502.
```

```
chore: upgrade dependencies to latest versions
```

## Guidelines

- If no changes are staged, ask the user to stage files first or offer to stage all changes.
- If the diff is large and spans multiple concerns, suggest splitting into separate commits.
- Prefer specificity over vagueness — "fix button alignment on mobile" beats "fix UI bug".
