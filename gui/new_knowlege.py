import json
import pathlib
import re

import PySimpleGUI as gui


class IDException(Exception):
    pass


def get_new_relation(number, relation_number) -> list[list[gui.Element]]:
    return [[gui.Combo(["is-Acronym", "is-Synonym", "has", "is", "part-of", "use", "defines", "contains"], "",
                       key=f"element-{number}-relation_type-{relation_number}"),
             gui.Input("", key=f"element-{number}-relation-{relation_number}")]]


def new_knowledge_element(number: int) -> gui.Frame:
    layout = [
        [gui.Text("TYP:"),
         gui.DropDown(["Term", "Definition", "Fact", "Exercise", "Example", "Code", "Question", "Answer"], "Term",
                      key=f"element-{number}-type")],
        [gui.Text("Name/ID:", tooltip="Die ID setzt sich aus dem Input und der ID zusammen"),
         gui.Input("", key=f"element-{number}-name", tooltip="Die ID setzt sich aus dem Input und der ID zusammen")],
        [gui.Text("Inhalt:"), gui.Multiline("", key=f"element-{number}-content", size=(35, 3))],
        [gui.Frame("Relations",
                   get_new_relation(number, 1), key=f"Frame-{number}-relations")],
        [gui.Button("Weitere Relation", key=f"new-relation-{number}")]]
    return gui.Frame("", layout=layout, key=f"Frame-element-{number}")


def create_knowledge_window() -> gui.Window:
    layout = [[gui.Frame("Elemente", [[new_knowledge_element(1)]], key="Frame-elements")],
              [gui.Button("Neues Element", key="new-element"), gui.Input("", key="output-name"),
               gui.Button("Speichern", key="save"), gui.Button("Neuer Wissenssatz", key="new-knowledge-set",
                                                               tooltip="Neues leres Fenster um neuen Wissenssatz zu erstellen.")]]
    return gui.Window("Neues Wissen", layout=[[gui.Column(layout=layout, size=(650, 300), expand_x=True, expand_y=True,
                                                          scrollable=True, vertical_scroll_only=True,
                                                          vertical_alignment="t")]],
                      resizable=True, auto_size_text=True)


def create_relations(keys: list, values: dict) -> list:
    back = []
    count = 0
    while count < len(keys):
        if "" not in [values[keys[count]], values[keys[count + 1]]]:
            back.append({"relation_id": values[keys[count + 1]], "relation_type": values[keys[count]]})
        count += 2
    return back


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
                       create_relations(keys[3:], values)
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


def run_new_knowledge(window: gui.Window):
    event: str
    n = 1
    while True:
        event, values = window.read()
        if event in [gui.WIN_X_EVENT, gui.WIN_CLOSED]:
            window.disable()
            answer, _ = gui.Window('Neues Wissensset?', [[gui.T('Soll das bestehende Wissen gespeichert werden?')],
                                                         [gui.Yes(s=10), gui.No(s=10), gui.Cancel(s=10)]],
                                   disable_close=True).read(close=True)
            if answer == "Yes":
                try:
                    save(values)
                except IDException:
                    window.enable()
                    continue
                gui.popup_ok("Datei wurde gespeichert!")
                window.close()
                break
            elif answer == "No":
                window.close()
                break
            window.enable()
        elif re.match(r"new-relation-\d+", event):
            number = int(event.split('-')[2])
            frame: gui.Frame = window.find_element(f"Frame-{number}-relations")
            relation_number = len(frame.widget.children) + 1
            window.extend_layout(frame, get_new_relation(number, relation_number))
        elif event == "new-element":
            frame = window.find_element("Frame-elements")
            number = len(frame.widget.children)
            window.extend_layout(frame, [[new_knowledge_element(number + 1)]])
        elif event == "save":
            try:
                save(values)
            except IDException:
                continue
            window.disable()
            gui.popup_ok("Datei wurde gespeichert!")
            window.enable()
        elif event == "new-knowledge-set":
            # answer = gui.popup("Soll die aktuelle datei gespeichert werden?")
            window.disable()
            answer, _ = gui.Window('Neues Wissensset?', [[gui.T('Soll das bestehende Wissen gespeichert werden?')],
                                                         [gui.Yes(s=10), gui.No(s=10), gui.Cancel(s=10)]],
                                   disable_close=True).read(close=True)
            window.enable()
            if answer == "Yes":
                try:
                    save(values)
                except IDException:
                    continue
                window.close()
                gui.popup_ok("Datei wurde gespeichert!")
                window = create_knowledge_window()
            elif answer == "No":
                window.close()
                window = create_knowledge_window()
        else:
            print("Unbekanntes Event! Abbruch")
            window.close()
        old_size = window.size
        n *= -1
        window.size = (old_size[0], old_size[1] + n)
