import json
import pathlib
import re

import PySimpleGUI as gui

from gui.new_knowledge import create_knowledge_element, IDException, parse_relations


def create_structure_window() -> gui.Window:
    layout = [[gui.Frame("Elemente", [[create_knowledge_element(1)]], key="Frame-elements")],
              [gui.Button("Neues Element", key="new-element"), gui.Input("", key="output-name"),
               gui.Button("Speichern", key="save"), gui.Button("Neuer Wissenssatz", key="new-knowledge-set",
                                                               tooltip="Neues leres Fenster um neuen Wissenssatz zu erstellen.")]]
    return gui.Window("Neue WissenElemente/Struktur",
                      layout=[[gui.Column(layout=layout, size=(650, 300), expand_x=True, expand_y=True,
                                          scrollable=True, vertical_scroll_only=True,
                                          vertical_alignment="t")]],
                      resizable=True, auto_size_text=True)


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
        if values[keys[1]] == "":
            gui.popup_error(f"Element {group} hat keine ID. Bitte angeben", title="Fehlende ID")
            raise IDException
        element = {"type": values[keys[0]].upper(),
                   "id": f"{values[keys[1]]}-{values[keys[0]].upper()}",
                   "content": values[keys[2]],
                   "relations":
                       parse_relations(keys[3:], values)
                   }
        elements.append(element)
    file_str = json.dumps(elements)
    path = pathlib.Path("./files/config.json")
    with open(path, "r") as config:
        output_path_base = pathlib.Path(json.loads(config.read())["path-to-output"])
    output_file_path = output_path_base.joinpath(f"{values['output-name']}.json")
    if output_file_path.name == ".json":
        output_file_path = output_path_base.joinpath("knowledge.json")
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


def run_new_structure(window: gui.Window):
    return None
