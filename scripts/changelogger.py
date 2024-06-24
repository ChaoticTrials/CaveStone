import json
import os
import shutil
import subprocess
import urllib.request

MODLISTCREATOR_VERSION = "4.1.1"
OUTPUT_PATH = "changelog"
REPOSITORY = "ChaoticTrials/CaveStone"


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


def create_changelog():
    subprocess.check_call(
        ["java", "-jar", f"{OUTPUT_PATH}/mlc.jar", "changelog",
         "--old", f"{OUTPUT_PATH}/old.mrpack",
         "--new", f"{OUTPUT_PATH}/new.mrpack",
         "--output", "./changelog.md"]
    )


def append_modlist():
    subprocess.check_call(
        ["java", "-jar", f"{OUTPUT_PATH}/mlc.jar", "modlist",
         "--no-header",
         "--output", "./modlist.md",
         f"{OUTPUT_PATH}/new.mrpack"]
    )
    with open("./modlist.md", "r", encoding="utf-8") as f:
        modlist = f.read()

    with open("./changelog.md", "a", encoding="utf-8") as f:
        f.write("# Modlist\n\n")
        f.write(modlist)


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

    print("Create the changelog")
    create_changelog()

    print("Appending modlist to changelog")
    append_modlist()


if __name__ == "__main__":
    main()