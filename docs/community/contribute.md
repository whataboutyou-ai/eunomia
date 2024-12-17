## Code Contribution

### Your development branch
First, [fork][github-fork] the `eunomia` repository and then clone your forked repository locally:

```bash
# HTTPS
git clone https://github.com/<YOUR_GITHUB_USERNAME>/eunomia.git

# SSH
git clone git@github.com:<YOUR_GITHUB_USERNAME>/eunomia.git
```

Once in the cloned repository directory, make a branch with your username and description of the pull request:

```bash
git checkout -B <YOUR_GITHUB_USERNAME>/<PR_DESCRIPTION>
```

### Python environment
Install the required dependecies with [poetry][poetry-home] including the development dependencies:

```bash
poetry install --with dev
```

### Testing and formatting
Before pushing your changes, ensure the tests pass and the code style aligns:

```bash
poetry run pytest
poetry run black .
poetry run isort --profile black .
```

*Note: a GitHub workflow will check the tests and formatting and reject the PR if it doesn't pass, so please make sure it passes locally.*


## Improving the Documentation
Install the required dependecies with [poetry][poetry-home] including the documentation dependencies:

```bash
poetry install --with docs
```

To build the documentation and serve it locally, run the following command in the repository's root folder:

```bash
mkdocs serve
```

In this way, you will be able to view the documentation locally. It will update every time you make a change.

## Open a Pull Request
We actively welcome your pull requests. The workflow is as follows:

1. Create your new branch from main in your forked repo, with your username and a name describing the work you're completing, e.g., `user1/new-feature-x` [[*go to details*](#your-development-branch)].
2. If you've added code that should be tested, add tests. Ensure all tests pass and your code lints [[*go to details*](#testing-and-formatting)].
3. If you've changed APIs or you want to add examples, update the documentation [[*go to details*](#improving-the-documentation)].
4. Open a [pull request][eunomia-pulls].

[github-fork]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo
[poetry-home]: https://python-poetry.org/
[eunomia-pulls]: https://github.com/whataboutyou-ai/eunomia/pulls
