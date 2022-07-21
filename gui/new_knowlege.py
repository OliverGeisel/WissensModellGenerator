import json
import pathlib
import re

import PySimpleGUI as gui


def new_knowlege_element(number: int) -> gui.Frame:
    layout = [
        [gui.Text("TYP:"),
         gui.DropDown(["Term", "Definition", "Synonym", "Fact", "Acronym"], "Term", key=f"element-{number}-type")],
        [gui.Text("Name:"), gui.Input("", key=f"element-{number}-name")],
        [gui.Text("Inhalt:"), gui.Input("", key=f"element-{number}-content")],
        [gui.Frame("Relations", [[gui.Input("", key=f"element-{number}-relation-1")]],
                   key=f"Frame-{number}-relations")],
        [gui.Button("Weitere Relation", key=f"new-relation-{number}")]]
    return gui.Frame("", layout=layout, key=f"Frame-element-{number}")


def create_knowledge_window() -> gui.Window:
    layout = [[gui.Frame("Elemente", [[new_knowlege_element(1)]], key="Frame-elements")],
              [gui.Button("Neues Element", key="new-element"), gui.Input("", key="output-name"),
               gui.Button("Speichern", key="save")]]
    return gui.Window("Neues Wissen", layout)


def save(values: dict[str, str]):
    elements = []
    elem_key = [key for key in values if key.startswith("element")]
    element_groups = dict()
    for key in elem_key:
        number = key.split("-")[1]
        if number not in element_groups:
            element_groups[number] = list()
        element_groups[number].append(key)

    for group, keys in element_groups.items():
        element = {"type": values[keys[0]],
                   "id": values[keys[1]],
                   "content": values[keys[2]],
                   "relations": [values[rel] for rel in keys[3:]]
                   }
        elements.append(element)
    file_str = json.dumps(elements)
    path = pathlib.Path("./files/config.json")
    with open(path, "r") as config:
        output_path_base = pathlib.Path(json.loads(config.read())["path-to-output"])
    output_file_path = output_path_base.joinpath(f"{values['output-name']}.json")
    count = 1
    if not output_path_base.exists():
        output_path_base.mkdir(parents=True)
    while output_file_path.exists():
        print("Datei existiert bereits! Wird umbenannt!")
        old_name = str(output_file_path.absolute()).removesuffix('.json')
        if re.search(r"(.*)(\(\d+\))", old_name) is not None:
            old_name = re.search(r"(.*)(\(\d+\))", old_name)[1]
        output_file_path = pathlib.Path(f"{old_name}({count}).json")
        count += 1
    with open(output_file_path, "w") as output_file:
        output_file.write(file_str)


def run_new_knowledge(window: gui.Window):
    event: str
    while True:
        event, values = window.read()
        if event in [gui.WIN_X_EVENT, gui.WIN_CLOSED]:
            break
        if re.match(r"new-relation-\d+", event):
            number = int(event.split('-')[2])
            frame: gui.Frame = window.find_element(f"Frame-{number}-relations")
            relation_number = len(frame.widget.children) + 1
            window.extend_layout(frame, [[gui.Input("", key=f"relation-{number}-{relation_number}")]])
        if event == "new-element":
            frame = window.find_element("Frame-elements")
            number = len(frame.widget.children)
            window.extend_layout(frame, [[new_knowlege_element(number + 1)]])
        if event == "save":
            save(values)
            window.disable()
            gui.popup_ok("Datei wurde gespeichert!")
            window.enable()
