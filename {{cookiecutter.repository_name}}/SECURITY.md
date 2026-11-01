# Security Policy

A Smarter Extension runs inside the Smarter platforms that install it, with access to their
settings and Secrets, so security reports are this project's highest priority.

## Reporting a Vulnerability

**Please do not report security vulnerabilities in public GitHub issues, discussions or pull
requests.**

Report them privately, with GitHub's private vulnerability reporting: open the repository's
[Security tab](https://github.com/{{ cookiecutter.github_owner }}/{{ cookiecutter.repository_name }}/security)
and choose **Report a vulnerability**. Or email
[{{ cookiecutter.author_email }}](mailto:{{ cookiecutter.author_email }}).

Please include the affected versions, the impact, and steps to reproduce.

A vulnerability in the Smarter platform itself goes to
[smarter-sh/smarter](https://github.com/smarter-sh/smarter/security).

## Supported Versions

Only the latest release is supported. A fix is released as a new version, which the
[Smarter Extension registry](https://github.com/smarter-sh/extensions-registry) offers to every
platform that has the extension installed.
