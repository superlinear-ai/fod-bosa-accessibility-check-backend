# Accessibility Check Backend

Extra checks for FOD BOSA's Accessibility Check tool.

Developed by [Radix](https://www.radix.ai).

## Deployment

It's very easy to deploy this API anywhere using [Docker](https://www.docker.com/get-started). Make sure you have Docker running.

1. First, we need to build the image:

    ```bash
    DOCKER_BUILDKIT=1 docker build --ssh default --target app-image --tag accessibility-check-backend-app .
    ```

    Note: we use [BuildKit](https://docs.docker.com/develop/develop-images/build_enhancements) to build our image.

2. To run the image locally, you can simply run the following command:

    ```bash
    docker run --detach --name ac-container --publish 80:8000 app-image
    ```

    This command runs the `app-image` image in a detached mode and publishes it on port 80.

3. You can now find the API at http://0.0.0.0.

    Tip: you can also open the link in the browser to test the API using the handy docs.

Instead of running the Docker image locally, you can also run it on a server. The easiest way to do this is pushing the container image you just built to a repository, and then pulling that image on your server.

## Contributing

### Development environment setup

<details>
<summary>Once per machine</summary>

1. [Generate an SSH key for GitHub and add it to your authentication agent](https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent). Then, [add the newly created SSH key to GitHub](https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account).
2. Install [Docker](https://www.docker.com/get-started).
3. Install [VS Code](https://code.visualstudio.com/) (optional).
4. Install [VS Code's Remote-Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (optional).
5. Install [Fira Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) (optional).

</details>

<details open>
<summary>Once per repository</summary>

You can set up your development environment as a self-contained [development container](https://code.visualstudio.com/docs/remote/containers) with a single step. In VS Code, press <kbd>⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd>, select _Remote-Containers: Clone Repository in Container Volume..._ and enter:

```
github.com:radix-ai/fod-bosa-accessibility-check-backend.git
```

Alternatively, if you prefer to install your environment locally, run `./tasks/init.sh` from VS Code's Terminal.
</details>

### Common tasks

<details>
<summary>Activating the Python environment</summary>

1. Open any Python file in the project to load VS Code's Python extension.
2. Open a Integrated Terminal with <kbd>⌃</kbd> + <kbd>~</kbd> and you should see that the conda environment `accessibility-check-backend-env` is active.
3. Now you're ready to run any of tasks listed by `invoke --list`.

Note: if you're not using VS Code, running `conda activate accessibility-check-backend-env` will also work.

</details>

<details>
<summary>Serving the API locally</summary>

1. Activate the Python environment.
2. Run the API locally by `invoke serve`
3. The API will be served on http://127.0.0.1:8000. Opening this link in a browser will show you the handy docs.

</details>

<details>
<summary>Releasing a new version</summary>

1. Activate the Python environment.
2. Commit any (un)staged changes on your branch.
3. Run `invoke bump --part=[major|minor|patch|post]` to (a) update the version number, (b) commit the changes, and (c) tag the commit with a version identifier.
4. Your tags will be pushed to the remote next time you `git push` (because `push.followTags` is set to true in `.git/config`). Or push the tag manually with `git push origin v0.1.0`.
5. You can now `pip install git+https://github.com/radix-ai/fod-bosa-accessibility-check-backend.git@v0.1.0`.

</details>

## Contributors

- [Giel Dops](https://github.com/gield)
- [Jérôme Renaux](https://github.com/Jerenaux)
