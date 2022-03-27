#!/usr/bin/env python3

import argparse
import csv
import sys

from os import environ
from snyk import SnykClient
from snykv3 import SnykV3Client

import snyk

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
        description="Generate a CSV of projects in a Snyk Organization or a set of "
                    "CSVs of projects for each Organization in a Group"
    )
    parser.add_argument(
        "--org-id",
        help="The organization ID from the Org's Setting panel",
        required=False,
    )
    parser.add_argument(
        "--group-id",
        help="The group ID from the Group's Settings panel",
        required=False,
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

    args = parser.parse_args()

    # validate arg combinations
    if args.org_id and args.group_id:
        sys.exit("1 of either --org-id or --group-id is required, but not both")
    
    if args.group_id and args.csv_file:
        sys.exit("--csv-file cannot be used with --group-id ")

    return args


def get_group_orgs(group_id, snyk_token):
    clientv1 = SnykClient(snyk_token, tries=2)

    orgs = clientv1.organizations.all()

    group_orgs = []

    for org in orgs:
        if org.group and org.group.id == group_id:
            group_orgs.append(org)
    return group_orgs

def build_csv(org_id, int_name, csv_file, tags, snyk_token):

    clientv1 = SnykClient(snyk_token, tries=2)
    clientv3 = SnykV3Client(snyk_token, tries=2)

    the_org = clientv1.organizations.get(org_id)

    org_name = the_org.name

    print(f"Getting all repos for {org_name}")

    targets = get_all_targets(org_id, clientv3, int_name)

    the_data = list()

    if len(targets) > 0:
        print(f"Searching for projects from {len(targets)} repo(s) in {org_name}")

        for target in targets:
    
            for project in get_all_projects(org_id, clientv3, tags, target):
                proj_attr = project["attributes"]
                proj_attr["repoName"] = target["attributes"]["displayName"]
                try:
                  v1_data = get_project_data(org_id, project["id"], clientv1)
                  the_data.append(proj_attr | v1_data)
                except snyk.errors.SnykHTTPError as error:
                  print(f"Error retrieving project, skipping...")
    
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

    clientv1 = SnykClient(snyk_token, tries=2)

    org_ids = []
    if (args.org_id):
        org_ids.append(args.org_id)
    if (args.group_id):
        # get all orgs in this group
        orgs = get_group_orgs(args.group_id, snyk_token)
        org_ids = [x.id for x in orgs]

    int_name = args.integration or "all"
    tags = args.tags or list()

    snyk_token = environ["SNYK_TOKEN"]

    if snyk_token == "BD832F91-A742-49E9-BC1E-411E0C8743EA":
        sys.exit("You didn't update example_secrets.sh with a valid token")

    if len(org_ids) > 1:
        print(f"{len(org_ids)} orgs to process")
        for org_id in org_ids:
            org_slug = [x.slug for x in orgs if x.id == org_id][0]
            csv_file = f"output/{int_name}_state.{org_slug}.csv"
            build_csv(org_id, int_name, csv_file, tags, snyk_token)
    else:
        csv_file = args.csv_file or f"output/{int_name}_state.csv"
        build_csv(org_ids[0], int_name, csv_file, tags, snyk_token)