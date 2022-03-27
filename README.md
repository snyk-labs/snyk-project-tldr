# project_tldr.py

This is an example python script to provide a tl;dr of all or some of the projects in a Snyk Organization or Group, allowing one to filter by integration type and/or tag. It will generate a csv [like this](example_output.csv)

## Requirements

This script requires a python environment with the Snyk, Github, and Typer libraries. Use the provided Dockerfile to build and run a container with this script setup in it. Refer to the [Docker](#user-content-running-with-docker) section for more information.

### Snyk Requirements

- Snyk Access Token: Either generate an service account token or [retrieve your own](https://docs.snyk.io/snyk-api-info/authentication-for-api)
- One of the following
  - Snyk Org ID: Available under the Settings view of the Org on [app.snyk.io](https://app.snyk.io/)
  - Snyk Group ID: Available under the Group Settings view of the Group on [app.snyk.io](https://app.snyk.io/)

### Environment Variables

While you can pass the Snyk token as a command-line argument to the script, it is best to use them as environment variables so they aren't stored in your workstation's command history.

Use [example_secrets.sh](example_secrets.sh) if you need a simple way to copy/paste your token into a file and then load them into your environment for use.

```shell
❯ python3 project_tldr.py -h
usage: project_tldr.py [-h] [--org-id ORG_ID] [--group-id GROUP_ID] [--integration INTEGRATION] [--csv-file CSV_FILE] [--tags TAGS [TAGS ...]]

Generate a CSV of projects in a Snyk Organization or a set of CSVs of projects for each Organization in a Group

optional arguments:
  -h, --help            show this help message and exit
  --org-id ORG_ID       The organization ID from the Org's Setting panel
  --group-id GROUP_ID   The group ID from the Group's Settings panel
  --integration INTEGRATION
                        Integration Name: bitbucket-cloud, github-enterprise, etc.
  --csv-file CSV_FILE   Complete path/to/file.csv to write the summary to: default output/$(integration-name)_state.csv
  --tags TAGS [TAGS ...]
                        Tags to filter with, in format: key=value
```

## Running with Docker

If you only have Docker and want to do this quickly, build this script into a container using the included dockerfile and it will configure itself for you and run. See the instructions for native installation in a Python3 environment using pip in the next [section](#running-with-python3-pip-version)

1. Build the container with docker, a command like this should suffice:

   ```shell
   ❯ docker build --pull --no-cache --force-rm -f Dockerfile -t project_tldr .
   [+] Building 42.0s (13/13) FINISHED
   => [internal] load build definition from Dockerfile
   => => transferring dockerfile: 586B
   => [internal] load .dockerignore
   => => transferring context: 2B
   => [internal] load metadata for docker.io/library/python:3.9-slim
   => [auth] library/python:pull token for registry-1.docker.io
   => [1/7] FROM docker.io/library/python:3.9-slim@sha256:e3c1da82791d701339381d90ae63843cf078fed94bae6f36f7abe3ed3e339218
   => [internal] load build context
   => => transferring context: 2.42kB
   => CACHED [2/7] WORKDIR /app
   => [3/7] COPY *.py .
   => [4/7] COPY requirements.txt .
   => [5/7] RUN python -m pip install --quiet -U pip
   => [6/7] RUN pip install --quiet -r requirements.txt
   => [7/7] RUN mkdir /app/output
   => exporting to image
   => => exporting layers
   => => writing image sha256:9f2e19772ead210472e576e7c2dc21b9e9c41bd0ac76af68679863513a9b4414
   => => naming to docker.io/library/project_tldr

   ```

2. Run the container with the `docker run` command, ensuring to:

   - Pass a local volume (`-v "${PWD}/output":/app/output`) for the csv output to be saved to
   - Pass the SNYK_TOKEN environment variable (`-e SNYK_TOKEN`)
   - Delete the container image after use (`--rm`)
   - Specify at minimum `--org-id` along with other options for the script

   ```shell
   ❯ docker run --rm -v "${PWD}/output":/app/output -e SNYK_TOKEN -it project_tldr \
   --org-id 1b48e2c4-6ca8-455f-a73f-d2f6f2a6b225
   Getting all repos for Angrydome
   Searching for projects from 30 repo(s) in Angrydome
   Saving 63 projects data to output/all_state.csv
   ```

3. An example output.csv should look something [like this](example_output.csv)

## Running with Python3 (pip version)

1. Using python3 create a virtual environment

   ```shell
   ❯ python3 -m venv .venv
   ❯ source .venv/bin/activate
   ❯ which python3
   /Users/chris/src/test_py/.venv/bin/python3
   ❯ python3 --version
   Python 3.9.10
   ```

2. Install pip and needed dependencies

   ```shell
   ❯ python3 -m pip install --quiet -U pip
   ❯ pip install -r requirements.txt
   ...
   Installing collected packages: msgpack, certifi, zipp, urllib3, typing-extensions, tomlkit, pyyaml, py, idna, decorator, charset-normalizer, retry, requests, poetry-version, mashumaro, importlib-metadata, pysnyk

   Successfully installed certifi-2021.10.8 charset-normalizer-2.0.11 decorator-5.1.1 idna-3.3 importlib-metadata-1.7.0 mashumaro-1.24 msgpack-1.0.3 poetry-version-0.1.5 py-1.11.0 pysnyk-0.6.3 pyyaml-6.0 requests-2.27.1 retry-0.9.2 tomlkit-0.5.11 typing-extensions-4.0.1 urllib3-1.26.8 zipp-3.7.0
   ```

3. Verify the command works

   ```shell
   ❯ python3 project_tldr.py --help
   usage: project_tldr.py [-h] --org-id ORG_ID [--integration INTEGRATION] [--csv-file CSV_FILE] [--tags TAGS [TAGS ...]]
   ...
   ```

4. A this point running the command is similar as the docker command with `python3 project_tldr.py --org-id` instead of the `docker run...` command

## Support

This script and its contents are provided as a best effort example of how to use Snyk and Github's python sdk's to generate data from both services APIs.

## License

[License: Apache License, Version 2.0](LICENSE)
