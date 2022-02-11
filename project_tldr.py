#!/usr/bin/env python3

import argparse
import csv

from os import environ
from snyk import SnykClient
from snykv3 import SnykV3Client

snyk_token = environ["SNYK_TOKEN"]

SCM_REPOS = (
    "azure-repos",
    "bitbucket-cloud",
    "bitbucket-server",
    "github",
    "github-enterprise",
    "gitlab",
)

KEEP_FIELDS = ("name", "browseUrl", "type", "testFrequency", "lastTestedDate", "origin")


def parse_command_line_args():
    parser = argparse.ArgumentParser(
        description="Generate a CSV of projects in a Snyk Organization"
    )
    parser.add_argument(
        "--org-id",
        help="The organization ID from the Org's Setting panel",
        required=True,
    )
    parser.add_argument(
        "--integration",
        help="Integration Name: bitbucket-cloud, github-enterprise, etc.",
    )
    parser.add_argument(
        "--csv-file",
        help="Complete path/to/file.csv to write the summary to: default output/$(integration-name)_state.csv",
    )
    parser.add_argument(
        "--tags", nargs="+", help="Tags to filter with, in format: key=value"
    )

    return parser.parse_args()


def build_csv(org_id, int_name, csv_file, tags, snyk_token):

    clientv1 = SnykClient(snyk_token, tries=2)
    clientv3 = SnykV3Client(snyk_token, tries=2)

    the_org = clientv1.organizations.get(org_id)

    org_name = the_org.name

    print(f"Getting all repos for {org_name}")

    targets = get_all_targets(org_id, clientv3, int_name)

    the_data = list()

    print(f"Searching for projects from {len(targets)} repo(s) in {org_name}")

    for target in targets:

        for project in get_all_projects(org_id, clientv3, tags, target):
            proj_attr = project["attributes"]
            proj_attr["repoName"] = target["attributes"]["displayName"]
            v1_data = get_project_data(org_id, project["id"], clientv1)
            the_data.append(proj_attr | v1_data)

    headers = [i for i in the_data[0].keys()]

    print(f"Saving {len(the_data)} projects data to {csv_file}")

    with open(csv_file, "w", newline="\n") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=headers, restval="", extrasaction="ignore"
        )

        writer.writeheader()
        for row in the_data:
            writer.writerow(row)


def get_all_targets(org_id, clientv3: SnykV3Client, int_name=None):
    # https://api.snyk.io/v3/orgs/orgId/targets?version=2021-08-20~beta&origin=github&isPrivate=true&remoteUrl=http%3A%2F%2Fgithub.com%2Fsnyk-fixtures%2Fgoof&excludeEmpty=false
    params = {}
    params["limit"] = 100

    if int_name not in ("all", None):
        params["origin"] = int_name

    return clientv3.get_all_pages(f"orgs/{org_id}/targets", params)


def get_all_projects(org_id, clientv3: SnykV3Client, tags, target: dict() = None):

    params = {"limit": 100, "status": "active"}

    if target != None:
        params["targetId"] = target["id"]

    if len(tags) > 0:
        params["tags"] = ":".join(tags)

    return clientv3.get_all_pages(f"orgs/{org_id}/projects", params)


def get_project_data(org_id, project_id, clientv1: SnykClient):

    proj_resp: dict = clientv1.get(f"org/{org_id}/project/{project_id}").json()

    proj = {k: v for k, v in proj_resp.items() if k in KEEP_FIELDS}

    issues = {f"issues_{k}": v for k, v in proj_resp["issueCountsBySeverity"].items()}

    proj.update(issues)

    if proj["origin"] in SCM_REPOS:
        # org/%s/project/%s/settings
        setting_resp: dict = clientv1.get(
            f"org/{org_id}/project/{project_id}/settings"
        ).json()
        proj.update(setting_resp)

    return proj


if __name__ == "__main__":
    args = parse_command_line_args()
    org_id = args.org_id or "1b48e2c4-6ca8-455f-a73f-d2f6f2a6b225"
    int_name = args.integration or "all"
    csv_file = args.csv_file or f"output/{int_name}_state.csv"
    tags = args.tags or list()

    snyk_token = environ["SNYK_TOKEN"]

    if snyk_token == "BD832F91-A742-49E9-BC1E-411E0C8743EA":
        print("You didn't update example_secrets.sh with a valid token")
        exit(1)

    build_csv(org_id, int_name, csv_file, tags, snyk_token)
