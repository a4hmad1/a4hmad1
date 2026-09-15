"""Refresh the public GitHub totals shown in the profile card."""

import os
import xml.etree.ElementTree as etree

import requests


USERNAME = os.getenv("USER_NAME", "a4hmad1")
TOKEN = os.getenv("ACCESS_TOKEN")
API = "https://api.github.com"


def headers():
    values = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        values["Authorization"] = f"Bearer {TOKEN}"
    return values


def github_get(path, params=None):
    response = requests.get(
        f"{API}{path}", headers=headers(), params=params, timeout=30
    )
    response.raise_for_status()
    return response


def public_stats():
    profile = github_get(f"/users/{USERNAME}").json()
    repos = []
    page = 1

    while True:
        batch = github_get(
            f"/users/{USERNAME}/repos",
            {"per_page": 100, "page": page, "type": "owner"},
        ).json()
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    return {
        "repo_data": profile["public_repos"],
        "star_data": sum(repo["stargazers_count"] for repo in repos if not repo["fork"]),
        "follower_data": profile["followers"],
    }


def update_svg(filename, stats):
    etree.register_namespace("", "http://www.w3.org/2000/svg")
    tree = etree.parse(filename)
    root = tree.getroot()

    for element_id, value in stats.items():
        element = root.find(f".//*[@id='{element_id}']")
        if element is not None:
            element.text = f"{value:,}"

    tree.write(filename, encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
    current = public_stats()
    update_svg("dark_mode.svg", current)
    print(
        f"Updated @{USERNAME}: {current['repo_data']} repos, "
        f"{current['star_data']} stars, {current['follower_data']} followers"
    )
