# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ruamel.yaml==0.19.1",
#     "requests==2.32.5",
# ]
# ///
import re
import sys
import requests
from ruamel.yaml import YAML

def get_latest_npm_version(package_name):
    """Fetch the latest version of an npm package."""
    try:
        response = requests.get(f"https://registry.npmjs.org/{package_name}/latest", timeout=10)
        response.raise_for_status()
        return response.json()["version"]
    except Exception as e:
        print(f"Error fetching npm version for {package_name}: {e}")
        return None

def get_latest_pypi_version(package_name):
    """Fetch the latest version of a PyPI package."""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        response.raise_for_status()
        return response.json()["info"]["version"]
    except Exception as e:
        print(f"Error fetching PyPI version for {package_name}: {e}")
        return None

def get_latest_github_release(owner, repo):
    """Fetch the latest release tag from a GitHub repository."""
    try:
        response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases/latest", timeout=10)
        if response.status_code == 404:
             # Fallback to tags if no releases
            response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/tags", timeout=10)
            response.raise_for_status()
            tags = response.json()
            if tags:
                return tags[0]["name"]
        response.raise_for_status()
        return response.json()["tag_name"]
    except Exception as e:
        print(f"Error fetching GitHub release for {owner}/{repo}: {e}")
        return None

def update_dependencies(file_path):
    yaml = YAML()
    yaml.preserve_quotes = True

    try:
        with open(file_path, "r") as f:
            data = yaml.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    updated = False

    if "repos" in data:
        for repo in data["repos"]:
            if "hooks" in repo:
                for hook in repo["hooks"]:
                    if "additional_dependencies" in hook:
                        new_deps = []
                        for dep in hook["additional_dependencies"]:
                            # Handle NPM packages (package@version)
                            npm_match = re.match(r"^(@?[a-z0-9-./]+)@(\d+\.\d+\.\d+)$", dep)
                            if npm_match:
                                package, current_version = npm_match.groups()
                                latest_version = get_latest_npm_version(package)
                                if latest_version and latest_version != current_version:
                                    print(f"Updating {package}: {current_version} -> {latest_version}")
                                    new_deps.append(f"{package}@{latest_version}")
                                    updated = True
                                else:
                                    new_deps.append(dep)
                                continue

                            # Handle PyPI packages (package==version)
                            pypi_match = re.match(r"^([a-zA-Z0-9-_]+)==(\d+\.\d+\.\d+)$", dep)
                            if pypi_match:
                                package, current_version = pypi_match.groups()
                                latest_version = get_latest_pypi_version(package)
                                if latest_version and latest_version != current_version:
                                    print(f"Updating {package}: {current_version} -> {latest_version}")
                                    new_deps.append(f"{package}=={latest_version}")
                                    updated = True
                                else:
                                    new_deps.append(dep)
                                continue

                            # Handle Go packages (github.com/owner/repo/...@version)
                            go_match = re.match(r"^(github\.com/([^/]+)/([^/]+)/?.*)@(v?\d+\.\d+\.\d+)$", dep)
                            if go_match:
                                full_path, owner, repo_name, current_version = go_match.groups()
                                latest_version = get_latest_github_release(owner, repo_name)
                                if latest_version and latest_version != current_version:
                                     # Ensure v-prefix consistency
                                    if current_version.startswith('v') and not latest_version.startswith('v'):
                                        latest_version = 'v' + latest_version
                                    elif not current_version.startswith('v') and latest_version.startswith('v'):
                                        latest_version = latest_version.lstrip('v')

                                    if latest_version != current_version:
                                        print(f"Updating {owner}/{repo_name}: {current_version} -> {latest_version}")
                                        new_deps.append(f"{full_path}@{latest_version}")
                                        updated = True
                                    else:
                                        new_deps.append(dep)
                                else:
                                    new_deps.append(dep)
                                continue

                            new_deps.append(dep)

                        hook["additional_dependencies"] = new_deps

    if updated:
        with open(file_path, "w") as f:
            yaml.dump(data, f)
        print(f"Updated {file_path}")
    else:
        print("No updates found.")

if __name__ == "__main__":
    update_dependencies(".pre-commit-config.yaml")
