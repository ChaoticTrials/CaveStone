import subprocess


def get_current_tag():
    try:
        current_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            universal_newlines=True
        ).strip()
        return current_tag
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while getting the current tag: {e}")
        return None


def get_previous_tag(current_tag):
    try:
        tags = subprocess.check_output(
            ["git", "tag", "--sort=-creatordate"],
            universal_newlines=True
        ).split()

        # Find the previous tag
        if current_tag in tags:
            current_index = tags.index(current_tag)
            if current_index + 1 < len(tags):
                return tags[current_index + 1]
        return None
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while getting the previous tag: {e}")
        return None
