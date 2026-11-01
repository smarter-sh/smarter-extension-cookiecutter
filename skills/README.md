# Agent Skills

This folder holds the [Agent Skills](https://agentskills.io/specification) for working on this
template with an AI coding agent such as Claude Code. `.claude/skills` is a symlink to it, so
Claude Code finds them. `CLAUDE.md`, at the repository's root, holds the rules for every task.

| Skill                                        | Use it when                                  |
| -------------------------------------------- | -------------------------------------------- |
| `smarter-extension-cookiecutter-development` | You're making any change. Start here.        |
| `smarter-extension-cookiecutter-git-commits` | You've been asked to write a commit message. |

The generated repository has its own skills, in `{{cookiecutter.repository_name}}/skills/`. They are
part of the template's output, and identical to the official extensions' skills. They are modeled
on the skills of [smarter-sh/smarter](https://github.com/smarter-sh/smarter/tree/main/skills).

## Security

A skill is a set of instructions that an agent follows, often without asking. The generated skills
reach every new extension's contributors, so review a change to either folder with the same care
as a change to a workflow: look for instructions unrelated to a skill's purpose, network calls in
scripts, and text that tells an agent to skip confirmations or safety rules. No keys or tokens.
