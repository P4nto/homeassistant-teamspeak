# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## GitLab is used for development

GitLab is used to host code and to track issues, feature requests and merge
requests. `master` and every release are mirrored to
[GitHub](https://github.com/P4nto/homeassistant-teamspeak) for the Home
Assistant Marketplace (formerly HACS).

Merge requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `master`.
2. If you've changed something, update the documentation.
3. Make sure your code lints and the tests pass.
4. Open a merge request!

## Development checks

The project uses [Ruff](https://docs.astral.sh/ruff/) and
[pytest-homeassistant](https://github.com/home-assistant/core/tree/dev/packages/pytest-homeassistant).

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest
```

The GitLab pipeline runs the same checks plus Hassfest.

## Release process

Releases are built by GitLab CI and mirrored to GitHub for the Marketplace.

1. Bump `version` in `custom_components/teamspeak/manifest.json` on a feature
   branch and merge it into `master`.
2. Create an annotated tag **on the merge commit that contains the version
   bump** and push it:

   ```bash
   git tag -a v0.5.3 -m "Teamspeak 3 Server v0.5.3"
   git push origin v0.5.3
   ```

3. The tag pipeline verifies that the tag matches the manifest version, creates
   the GitLab release with the integration archive and mirrors the tag and
   release to GitHub.

The `check-version` job fails the pipeline if the tag and `manifest.json`
differ, and both release jobs depend on it. Never tag a commit before its
version bump is merged.

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub [issues](https://github.com/P4nto/homeassistant-teamspeak/issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](https://github.com/P4nto/homeassistant-teamspeak/issues); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
