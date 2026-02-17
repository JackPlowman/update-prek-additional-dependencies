# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ruamel.yaml==0.19.1",
#     "requests==2.32.5",
# ]
# ///
import re
from pathlib import Path

import requests
from ruamel.yaml import YAML


def get_latest_npm_version(package_name: str) -> str | None:
    """Fetch the latest version of an npm package."""
    try:
        response = requests.get(
            f"https://registry.npmjs.org/{package_name}/latest", timeout=10
        )
        response.raise_for_status()
        return response.json()["version"]
    except requests.RequestException as e:
        print(f"Error fetching npm version for {package_name}: {e}")
        return None


def get_latest_pypi_version(package_name: str) -> str | None:
    """Fetch the latest version of a PyPI package."""
    try:
        response = requests.get(
            f"https://pypi.org/pypi/{package_name}/json", timeout=10
        )
        response.raise_for_status()
        return response.json()["info"]["version"]
    except requests.RequestException as e:
        print(f"Error fetching PyPI version for {package_name}: {e}")
        return None


def get_latest_github_release(owner: str, repo: str) -> str | None:
    """Fetch the latest release tag from a GitHub repository."""
    try:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/releases/latest", timeout=10
        )
        if response.status_code == 404:
            # Fallback to tags if no releases
            response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/tags", timeout=10
            )
            response.raise_for_status()
            tags = response.json()
            if tags:
                return tags[0]["name"]
        response.raise_for_status()
        return response.json()["tag_name"]
    except requests.RequestException as e:
        print(f"Error fetching GitHub release for {owner}/{repo}: {e}")
        return None


def check_npm_dependency(dep: str) -> str | None:
    """Check and return updated npm dependency."""
    npm_match = re.match(r"^(@?[a-z0-9-./]+)@(\d+\.\d+\.\d+)$", dep)
    if npm_match:
        package, current_version = npm_match.groups()
        latest_version = get_latest_npm_version(package)
        if latest_version and latest_version != current_version:
            print(f"Updating {package}: {current_version} -> {latest_version}")
            return f"{package}@{latest_version}"
    return None


def check_pypi_dependency(dep: str) -> str | None:
    """Check and return updated PyPI dependency."""
    pypi_match = re.match(r"^([a-zA-Z0-9-_]+)==(\d+\.\d+\.\d+)$", dep)
    if pypi_match:
        package, current_version = pypi_match.groups()
        latest_version = get_latest_pypi_version(package)
        if latest_version and latest_version != current_version:
            print(f"Updating {package}: {current_version} -> {latest_version}")
            return f"{package}=={latest_version}"
    return None


def check_go_dependency(dep: str) -> str | None:
    """Check and return updated Go dependency."""
    go_match = re.match(r"^(github\.com/([^/]+)/([^/]+)/?.*)@(v?\d+\.\d+\.\d+)$", dep)
    if not go_match:
        return None

    full_path, owner, repo_name, current_version = go_match.groups()
    latest_version = get_latest_github_release(owner, repo_name)

    if latest_version and latest_version != current_version:
        # Ensure v-prefix consistency
        if current_version.startswith("v") and not latest_version.startswith("v"):
            latest_version = "v" + latest_version
        elif not current_version.startswith("v") and latest_version.startswith("v"):
            latest_version = latest_version.lstrip("v")

        if latest_version != current_version:
            print(
                f"Updating {owner}/{repo_name}: {current_version} -> {latest_version}"
            )
            return f"{full_path}@{latest_version}"

    return None


def update_content_with_dependency(
    content: str, old_dep: str, new_dep: str
) -> tuple[str, bool]:
    """Replace dependency in content, handling quotes."""
    quotes = ['"', "'"]
    for q in quotes:
        quoted_dep = f"{q}{old_dep}{q}"
        if quoted_dep in content:
            return content.replace(quoted_dep, f"{q}{new_dep}{q}"), True

    # Fallback to unquoted replacement
    if old_dep in content:
        return content.replace(old_dep, new_dep), True

    return content, False


def process_dependencies(deps: list[str], content: str) -> tuple[str, bool]:
    """Process a list of dependencies and update content."""
    updated_content = content
    changes_made = False

    for dep in deps:
        new_dep = (
            check_npm_dependency(dep)
            or check_pypi_dependency(dep)
            or check_go_dependency(dep)
        )

        if new_dep:
            updated_content, replaced = update_content_with_dependency(
                updated_content, dep, new_dep
            )
            if replaced:
                changes_made = True

    return updated_content, changes_made


def update_dependencies(file_path: str) -> None:
    """Update dependencies in the specified file."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    content = path.read_text(encoding="utf-8")
    data = yaml.load(content)

    updated_content = content
    changes_made = False

    if "repos" in data:
        for repo in data["repos"]:
            if "hooks" in repo:
                for hook in repo["hooks"]:
                    if "additional_dependencies" in hook:
                        new_content, changed = process_dependencies(
                            hook["additional_dependencies"], updated_content
                        )
                        if changed:
                            updated_content = new_content
                            changes_made = True

    if changes_made:
        path.write_text(updated_content, encoding="utf-8", newline="\n")
        print(f"Updated {file_path}")
    else:
        print("No updates found.")


if __name__ == "__main__":
    update_dependencies(".pre-commit-config.yaml")
