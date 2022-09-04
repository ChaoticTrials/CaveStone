import json
import os
import shutil
import subprocess
import urllib.request

MODLISTCREATOR_VERSION = "4.0.2"
OUTPUT_PATH = "changelog"


def create_paths():
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)


def download_tools():
    urllib.request.urlretrieve(
        f"https://github.com/ModdingX/ModListCreator/releases/download/v{MODLISTCREATOR_VERSION}/ModListCreator-{MODLISTCREATOR_VERSION}-fatjar.jar",
        f"{OUTPUT_PATH}/mlc.jar")


def download_release():
    with urllib.request.urlopen("https://api.github.com/repos/MelanX/CaveStone/releases/latest") as url:
        data = json.loads(url.read().decode())

    for file in data["assets"]:
        if file["name"].endswith("-curse.zip"):
            urllib.request.urlretrieve(file["browser_download_url"], f"{OUTPUT_PATH}/old.zip")
            return


def create_export():
    if not os.name == "nt":
        subprocess.check_call(["chmod", "+x", "./gradlew"])

    if not os.path.exists("build/target") or len(os.listdir("build/target")) < 1:
        subprocess.check_call(["./gradlew", "buildCursePack"])


def copy_export():
    for file in os.listdir("build/target"):
        if file.endswith("-curse.zip"):
            print(f"Found {file}")
            shutil.copyfile("build/target/" + file, f"{OUTPUT_PATH}/new.zip")
        return


def create_changelog():
    subprocess.check_call(
        ["java", "-jar", f"{OUTPUT_PATH}/mlc.jar", "changelog",
         "--old", f"{OUTPUT_PATH}/old.zip",
         "--new", f"{OUTPUT_PATH}/new.zip",
         "--output", "./changelog.md"]
    )


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
    # create_changelog()


if __name__ == "__main__":
    main()
