import os
import shutil
import subprocess


def build_nodes():
    # todo should ensure correct directory

    data_path = "./data"
    only_files = [os.path.join(data_path, file)
                  for file in os.listdir(data_path)
                  if os.path.isfile(os.path.join(data_path, file))]
    print(only_files)
    lines = ["#!/bin/bash\n"]

    i = 0
    for file in only_files:
        i += 1
        shutil.copy(file, "./Node/data.csv")
        subprocess.run(f"docker build -t fls_node:1.{i} .", shell=True)
        os.remove("./Node/data.csv")
        lines.append(f"gnome-terminal --tab --title=\"Node_{i}\" "
                     f"--command=\"bash -c 'docker run -it --rm -p "
                     f"127.0.0.1:4030{i}:40400 fls_node:1.{i}; echo $SHELL'\"\n")

    with open("./launch_nodes.sh", "w") as launch_node_file:
        launch_node_file.writelines(lines)

    print("Complete with no errors")


if __name__ == '__main__':
    try:
        build_nodes()
    finally:
        try:
            os.remove("./Node/data.csv")
        except OSError:
            pass
