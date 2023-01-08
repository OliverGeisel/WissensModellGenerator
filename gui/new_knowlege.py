import re

import PySimpleGUI as gui

from core import save_as_file


class IDException(Exception):
    pass


def get_new_relation(number, relation_number) -> list[list[gui.Element]]:
    return [[gui.Combo(["is-Acronym", "is-Synonym", "has", "is", "part-of", "use", "defines", "contains"], "",
                       key=f"element-{number}-relation_type-{relation_number}"),
             gui.Input("", key=f"element-{number}-relation-{relation_number}")]]


def create_new_structure_child(structure_frame: gui.Frame):
    key = structure_frame.key.removesuffix("-children").removeprefix("structure-")
    element_num = len(structure_frame.widget.children)
    new_key = key + f"-{element_num}"
    frame = gui.Frame("", [[gui.Text("Name:"), gui.Input(key=f"structure-{new_key}-id")],
                           [gui.Column([[]], key=f"structure-{new_key}-children")],
                           [gui.Button("Neues Kindelement", key=f"add-{new_key}-child")]],
                      key=f"structure-{new_key}-structure-frame")
    back = [[frame]]
    return back


def add_structure_element(event, window):
    key = event.removeprefix("add-").removesuffix("-child")
    structure_frame = window.find_element(f"structure-{key}-children")
    window.extend_layout(structure_frame, create_new_structure_child(structure_frame))


def new_knowledge_element(number: int) -> gui.Frame:
    layout = [
        [gui.Text("TYP:", tooltip="Art des Wissens"),
         gui.DropDown(
             ["Term", "Definition", "Fact", "Proof", "Exercise", "Example", "Code", "Question", "Answer", "Node"],
             "Term", key=f"element-{number}-type")],
        [gui.Text("Name/ID:", tooltip="Die ID setzt sich aus dem Input und dem Typ zusammen"),
         gui.Input("", key=f"element-{number}-name", tooltip="Die ID setzt sich aus dem Input und dem Typ zusammen")],
        [gui.Text("Name/ID-Struktur-Element:", tooltip="Die ID des Strukturelements"),
         gui.Input("", key=f"element-{number}-structure-name",
                   tooltip="Die ID des Strukturelements")],
        [gui.Text("Inhalt:"), gui.Multiline("", key=f"element-{number}-content", size=(35, 3))],
        [gui.Frame("Relations",
                   get_new_relation(number, 1), key=f"Frame-{number}-relations")],
        [gui.Button("Weitere Relation", key=f"new-relation-{number}")]]
    return gui.Frame("", layout=layout, key=f"Frame-element-{number}")


def create_structure_column_layout():
    back = [[gui.Text("Area of Knowledge: "), gui.Input(key="structure-area-of-knowledge")],
            [gui.Frame("Area of Knwoledge Kindelemente", [[gui.Column([[]], key="structure-_root-children")]],
                       key="structure-_root-structure-frame")],
            [gui.Column([[gui.Button("Neues Kindelement", key="add-_root-child")]])]
            ]
    return back


def create_knowledge_window() -> gui.Window:
    structure_layout = create_structure_column_layout()
    layout = [[gui.Column([[gui.Frame("Elemente", [[new_knowledge_element(1)]], key="Frame-elements")]]),
               gui.Column([[gui.Frame("Struktur", structure_layout)]])],
              [gui.Button("Neues Element", key="new-element"), gui.Input("", key="output-name"),
               gui.Button("Speichern", key="save"), gui.Button("Neuer Wissenssatz", key="new-knowledge-set",
                                                               tooltip="Neues leeres Fenster, um neuen Wissenssatz zu erstellen.")]]
    return gui.Window("Neues Wissen", layout=[[gui.Column(layout=layout, size=(950, 300), expand_x=True, expand_y=True,
                                                          scrollable=True, vertical_scroll_only=True,
                                                          vertical_alignment="t")]],
                      resizable=True, auto_size_text=True)


def create_relations(keys: list, values: dict) -> list:
    back = []
    count = 1
    while count + 1 < len(keys):
        if "" not in [values[keys[count]], values[keys[count + 1]]]:
            back.append({"relation_id": values[keys[count + 1]], "relation_type": values[keys[count]]})
        count += 2
    return back


def parse_structure(id_keys, last_element, values):
    for key in id_keys:
        if re.match(r"\d+-id", key):
            new_last_element = {"key": last_element["key"] + "-" + key.removesuffix("-id"),
                                "id": values[f"structure-{last_element['key']}-{key}"],
                                "children": list()}
            last_element["children"].append(new_last_element)
            new_keys = [new_key.removeprefix(key.split("-")[0] + "-") for new_key in id_keys if
                        new_key.startswith(key.removesuffix("-id"))]
            parse_structure(new_keys, new_last_element, values)


def save(values: dict[str, str]):
    knowledge_model = dict()
    elements = []
    knowledge_model["knowledge"] = elements
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
                   "structure": values[keys[2]],
                   "content": values[keys[3]],
                   "relations":
                       create_relations(keys[4:], values)
                   }
        elements.append(element)
    # ------------------- STRUCTURE ---------------------------------------------------------------

    structure_keys = [key.removeprefix("structure-") for key in values if key.startswith("structure-")]
    id_keys = [key.removeprefix("_root-") for key in structure_keys if key.startswith("_root-")]
    area_of_knowledge = values['structure-area-of-knowledge']
    structure = {"area-of-knowledge": area_of_knowledge, "key": "_root", "children": list()}
    parse_structure(id_keys, structure, values)
    knowledge_model["structure"] = structure
    # ------------------- FINISH ------------------------------------------------------------------
    knowledge_model["sources"] = dict()
    save_as_file(knowledge_model, values, "knowledge")


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
            window.bring_to_front()
            if answer == "Yes":
                try:
                    save(values)
                except IDException:
                    continue
                window.close()
                gui.popup_ok("Datei wurde gespeichert!")
                window = create_knowledge_window()
                window.finalize()
            elif answer == "No":
                window.close()
                window = create_knowledge_window()
                window.finalize()
        elif re.match(r"add-[-_\w]*-child", event):
            add_structure_element(event, window)
        else:
            print("Unbekanntes Event! Abbruch!")
            window.close()
            break
        old_size = window.size
        n *= -1
        window.size = (old_size[0], old_size[1] + n)
    return
