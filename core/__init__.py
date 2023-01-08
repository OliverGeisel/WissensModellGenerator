import json
import pathlib
import re

import PySimpleGUI as gui


def save_as_file(model, values, base_file_name="file"):
    file_str = json.dumps(model)
    path = pathlib.Path("./files/config.json")
    with open(path, "r") as config:
        output_path_base = pathlib.Path(json.loads(config.read())["path-to-output"])
    output_file_path = output_path_base.joinpath(f"{values['output-name']}.json")
    if output_file_path.name == ".json":
        output_file_path = output_path_base.joinpath(f"{base_file_name}.json")
    count = 1
    if not output_path_base.exists():
        output_path_base.mkdir(parents=True)
    shown = False
    while output_file_path.exists():
        if not shown:
            gui.popup_ok("Datei existiert bereits! Wird umbenannt!")
            shown = True
        print("Datei existiert bereits! Wird umbenannt!")
        old_name = str(output_file_path.absolute()).removesuffix('.json')
        if re.search(r"(.*)(\(\d+\))", old_name) is not None:
            old_name = re.search(r"(.*)(\(\d+\))", old_name)[1]
        output_file_path = pathlib.Path(f"{old_name}({count}).json")
        count += 1
    with open(output_file_path, "w") as output_file:
        output_file.write(file_str)
