/**
 * semantic-release, run by .github/workflows/release.yml on each push to main.
 *
 * It reads the conventional commits since the last v* tag: a fix or perf releases a patch, a feat a
 * minor version, and a BREAKING CHANGE a major version. It adds the release's notes to
 * CHANGELOG.md, commits it, tags the commit v<version>, and creates the GitHub release. The tags
 * let extension authors generate from a known version of the template:
 *
 *   cookiecutter gh:smarter-sh/smarter-extension-cookiecutter --checkout v1.2.0
 */
module.exports = {
  branches: ["main"],
  tagFormat: "v${version}",
  plugins: [
    [
      "@semantic-release/commit-analyzer",
      {
        preset: "conventionalcommits",
        releaseRules: [
          { type: "docs", release: false },
          { type: "test", release: false },
          { type: "style", release: false },
          { type: "refactor", release: false },
        ],
        parserOpts: {
          noteKeywords: ["BREAKING CHANGE", "BREAKING CHANGES"],
        },
      },
    ],
    [
      "@semantic-release/release-notes-generator",
      {
        preset: "conventionalcommits",
        presetConfig: {
          types: [
            { type: "feat", section: "Features", hidden: false },
            { type: "fix", section: "Bug Fixes", hidden: false },
            { type: "refactor", section: "Refactoring", hidden: false },
            { type: "perf", section: "Performance", hidden: false },
          ],
        },
      },
    ],
    ["@semantic-release/changelog", { changelogFile: "CHANGELOG.md", changelogTitle: "# Changelog" }],
    [
      "@semantic-release/git",
      {
        assets: ["CHANGELOG.md"],
        message: "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
      },
    ],
    ["@semantic-release/github", { successComment: false, failComment: false, releasedLabels: false }],
  ],
};
