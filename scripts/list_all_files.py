import os


def main(folder):
    for path, subdirs, files in os.walk(folder):
        for name in files:
            if name.endswith(".zip"):
                print(os.path.join(path, name))


if __name__ == "__main__":
    main("../")
