# Accessibility Check Backend

Extra checks for FOD BOSA's Accessibility Check tool.

The frontend for this tool can be found [here](https://github.com/radix-ai/AccessibilityCheck).

We have created a list of improvements [here](docs/future_improvements.md).

General project documentation can be found in the [docs folder](docs/).

## Installation

To install this package in your environment, run:

```bash
pip install git+ssh://git@gitlab.com/radix-ai/fod-bosa/accessibility-check-backend.git@v0.2.0
```

## Deployment

It's easy to deploy this API anywhere using [Docker](https://www.docker.com/get-started). Make sure you have Docker running.

1. First, we need to build the image:

    ```bash
    DOCKER_BUILDKIT=1 docker build --ssh default --target app-image --tag accessibility-check-backend-app .
    ```

    Note: we use [BuildKit](https://docs.docker.com/develop/develop-images/build_enhancements) to build our image.
    
    Note: in case the Docker build crashes, you may need to increase the amount of RAM allowed to Docker.

2. To run the image locally, you can simply run the following command:

    ```bash
    docker run --detach --name ac-container --publish 80:8000 accessibility-check-backend-app
    ```

    This command runs the `app-image` image in a detached mode and publishes it on port 80.

3. You can now find the API at http://0.0.0.0.

    Tip: you can also open the link in the browser to test the API using the handy docs.

Instead of running the Docker image locally, you can also run it on a server. The easiest way to do this is pushing the container image you just built to a repository, and then pulling that image on your server.

## Contributing

### Development environment setup

<details>
<summary>Once per machine</summary>

1. [Generate an SSH key](https://docs.gitlab.com/ee/ssh/README.html#generating-a-new-ssh-key-pair) for GitLab, [add the SSH key to GitLab](https://docs.gitlab.com/ee/ssh/README.html#adding-an-ssh-key-to-your-gitlab-account), and [add the SSH key to your authentication agent](https://docs.gitlab.com/ee/ssh/README.html#working-with-non-default-ssh-key-pair-paths).
2. Install [Docker](https://www.docker.com/get-started).
3. Install [VS Code](https://code.visualstudio.com/).
4. Install [VS Code's Remote-Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).
5. Install [Fira Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) (optional).

</details>

<details open>
<summary>Once per repository</summary>

You can set up your development environment as a self-contained [development container](https://code.visualstudio.com/docs/remote/containers) with a single step. In VS Code, press <kbd>⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd>, select _Remote-Containers: Clone Repository in Container Volume..._ and enter:

```
git@gitlab.com:radix-ai/fod-bosa/accessibility-check-backend.git
```

Alternatively, if you prefer to install your environment locally, run `./tasks/init.sh` from VS Code's Terminal.
</details>

### Common tasks

<details>
<summary>Activating the Python environment</summary>

1. Open any Python file in the project to load VS Code's Python extension.
2. Open a Integrated Terminal with <kbd>⌃</kbd> + <kbd>~</kbd> and you should see that the conda environment `accessibility-check-backend-env` is active.
3. Now you're ready to run any of tasks listed by `invoke --list`.

</details>

<details>
<summary>Running and debugging tests</summary>

1. Activate the Python environment.
2. If you don't see _⚡ Run tests_ in the blue bar, run <kbd>⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> > _Python: Discover Tests_. Optionally debug the output in _View_ > _Output_ > _Python Test Log_ in case this step fails.
3. Go to any test function in `src/tests/pytest`.
4. Optional: put a breakpoint 🔴 next to the line number where you want to stop.
5. Click on _Run Test_ or _Debug Test_ above the test you want to debug.

</details>

<details>
<summary>Releasing a new version</summary>

1. Activate the Python environment.
2. Commit any (un)staged changes on your branch and make sure to test them with `invoke test`.
3. Run `invoke bump --part=[major|minor|patch|post]` to (a) update the version number, (b) commit the changes, and (c) tag the commit with a version identifier.
4. Your tags will be pushed to the remote next time you `git push` (because `push.followTags` is set to true in `.git/config`). Or push the tag manually with `git push origin v0.2.0`.
5. You can now `pip install git+ssh://git@gitlab.com/radix-ai/fod-bosa/accessibility-check-backend.git@v0.2.0`.

</details>

<details>
<summary>Updating the Cookiecutter scaffolding</summary>

1. Activate the Python environment.
2. Run `cruft check` to check for updates.
3. Run `cruft update` to update to the latest scaffolding.
4. Address failed merges in any `.rej` files.

</details>
