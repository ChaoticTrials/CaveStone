import json
import os
import shutil
import subprocess
import urllib.request

import github_utils

MODLISTCREATOR_VERSION = "4.1.2"
OUTPUT_PATH = "changelog"
REPOSITORY = "ChaoticTrials/CaveStone"
COMMITS_CHANGELOG_FILE = 'commits_changelog.md'
MODS_CHANGELOG_FILE = 'mods_changelog.md'
MODLIST_FILE = 'modlist.md'

GITHUB_CHANGELOG = 'github_changelog.md'
MODRINTH_CHANGELOG = 'modrinth_changelog.md'


def create_paths():
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)


def download_tools():
    urllib.request.urlretrieve(
        f"https://github.com/ModdingX/ModListCreator/releases/download/v{MODLISTCREATOR_VERSION}/ModListCreator-{MODLISTCREATOR_VERSION}-fatjar.jar",
        f"{OUTPUT_PATH}/mlc.jar")


def download_release():
    with urllib.request.urlopen(f"https://api.github.com/repos/{REPOSITORY}/releases/latest") as url:
        data = json.loads(url.read().decode())

    for file in data["assets"]:
        if file["name"].endswith("-modrinth.mrpack"):
            urllib.request.urlretrieve(file["browser_download_url"], f"{OUTPUT_PATH}/old.mrpack")
            return


def create_export():
    if not os.name == "nt":
        subprocess.check_call(["chmod", "+x", "./gradlew"])

    if not os.path.exists("build/target") or len(os.listdir("build/target")) < 1:
        subprocess.check_call(["./gradlew", "buildModrinthPack"])


def copy_export():
    for file in os.listdir("build/target"):
        if file.endswith("-modrinth.mrpack"):
            print(f"Found {file}")
            shutil.copyfile("build/target/" + file, f"{OUTPUT_PATH}/new.mrpack")
            return


def generate_commits_changelog():
    current_tag = github_utils.get_current_tag()
    if not current_tag:
        print("Could not determine the current tag.")
        return

    previous_tag = github_utils.get_previous_tag(current_tag)
    if not previous_tag:
        print("Could not determine the previous tag.")
        return

    try:
        # Get the commit messages between the two tags
        commit_log = subprocess.check_output(
            ["git", "log", f"{previous_tag}..{current_tag}", "--pretty=format:- %s"],
            universal_newlines=True
        )

        with open(COMMITS_CHANGELOG_FILE, 'w') as f:
            f.write(commit_log + '\n')

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while generating the changelog: {e}")


def generate_mod_changelog(no_header: bool = False):
    args = ["java", "-jar", f"{OUTPUT_PATH}/mlc.jar", "changelog",
            "--old", f"{OUTPUT_PATH}/old.mrpack",
            "--new", f"{OUTPUT_PATH}/new.mrpack",
            "--output", MODS_CHANGELOG_FILE]
    if no_header:
        args.insert(4, "--no-header")
    subprocess.check_call(args)


def generate_modlist():
    subprocess.check_call(
        ["java", "-jar", f"{OUTPUT_PATH}/mlc.jar", "modlist",
         "--no-header",
         "--output", MODLIST_FILE,
         f"{OUTPUT_PATH}/new.mrpack"]
    )


def append_file(target: str, file: str, title: str = None, spoiler: bool = False):
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()

    with open(target, "a", encoding="utf-8") as f:
        if spoiler:
            f.write(f'<details><summary>{title if title else 'Spoiler'}</summary>\n\n')
        elif title:
            f.write(f"# {title}\n\n")
        f.write(content + '\n')
        if spoiler:
            f.write('\n\n</details>\n\n')


def main():
    print("Create paths")
    create_paths()

    print("Download required tools")
    download_tools()

    print("Download the latest modpack release")
    download_release()

    print("Create the modpack export if not existing")
    create_export()

    print("Copy the modpack export to changelog path")
    copy_export()

    print("Generate commits changelog")
    generate_commits_changelog()

    print("Generate modlist")
    generate_modlist()

    print("Summarize github changelog")
    generate_mod_changelog(no_header=False)
    append_file(GITHUB_CHANGELOG, MODS_CHANGELOG_FILE)
    append_file(GITHUB_CHANGELOG, MODLIST_FILE, title='Modlist')

    print("Summarize modrinth changelog")
    generate_mod_changelog(no_header=True)
    append_file(MODRINTH_CHANGELOG, COMMITS_CHANGELOG_FILE)
    append_file(MODRINTH_CHANGELOG, MODS_CHANGELOG_FILE, title='Mod changes', spoiler=True)
    append_file(MODRINTH_CHANGELOG, MODLIST_FILE, title='Modlist', spoiler=True)


if __name__ == "__main__":
    main()
