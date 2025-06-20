## Code Contribution

### Your development branch

First, [fork][github-fork] the `eunomia` repository and then clone your forked repository locally:

=== "HTTPS"
    ```bash
    git clone https://github.com/<YOUR_GITHUB_USERNAME>/eunomia.git
    ```

=== "SSH"
    ```bash
    git clone git@github.com:<YOUR_GITHUB_USERNAME>/eunomia.git
    ```

Once in the cloned repository directory, make a branch with your username and description of the pull request:

```bash
git checkout -B <YOUR_GITHUB_USERNAME>/<PR_DESCRIPTION>
```

### Python environment

Install the required dependecies with [uv][uv-home]:

```bash
uv sync
```

If you are developing one of the additional packages (SDKs or extensions), you can install the dependencies for all packages:

```bash
uv sync --all-packages
```

### Testing and formatting

Before pushing your changes, ensure the tests pass and the code style aligns:

```bash
uv run pytest
uv run ruff check
uv run ruff format --check
```

_Note: a GitHub workflow will check the tests and formatting and reject the PR if it doesn't pass, so please make sure it passes locally._

## Improving the Documentation

Install the required dependecies with [uv][uv-home] including the documentation dependencies:

```bash
uv sync --group docs --all-packages
```

To build the documentation and serve it locally, run the following command in the repository's root folder; the documentation will update every time you make a change:

```bash
uv run mkdocs serve
```

The documentation is built with [Material for MkDocs][material-mkdocs-home], refer to their documentation for more information on how to use it.

## Open a Pull Request

We actively welcome your pull requests; this is the workflow you should follow:

| Step | Description                                          | Jump to                                                           |
| ---- | ---------------------------------------------------- | ----------------------------------------------------------------- |
| 1    | Create your new branch from main in your forked repo | [:material-arrow-up: Branch Setup](#your-development-branch)      |
| 2    | Add tests, if needed, and ensure all tests pass      | [:material-arrow-up: Testing](#testing-and-formatting)            |
| 3    | Update documentation for API changes                 | [:material-arrow-up: Documentation](#improving-the-documentation) |
| 4    | Open a pull request                                  | [:material-arrow-top-right: GitHub PRs][eunomia-pulls]            |

[github-fork]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo
[uv-home]: https://docs.astral.sh/uv/
[eunomia-pulls]: https://github.com/whataboutyou-ai/eunomia/pulls
[material-mkdocs-home]: https://squidfunk.github.io/mkdocs-material/
