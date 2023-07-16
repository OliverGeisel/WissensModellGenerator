import re

import PySimpleGUI as gui

from core import save, IdException
from gui.new_structure import create_structure_column_layout, add_structure_element

RELATION_TYPES = (
    "is-Acronym-for", "is-Synonym-for", "has", "is", "part-of", "use", "defines", "contains", "proofs", "related")
ELEMENT_TYPES = (
    "Term", "Definition", "Fact", "Proof", "Exercise", "Statement", "Example", "Code", "Question", "Answer", "Node")


def create_new_relation(number: int, relation_number: int) -> list[list[gui.Element]]:
    return [[gui.Combo(RELATION_TYPES, "",
                       key=f"element-{number}-relation_type-{relation_number}"),
             gui.Input("", key=f"element-{number}-relation-{relation_number}"),
             gui.DropDown(ELEMENT_TYPES, ELEMENT_TYPES[0], key=f"element-{number}-relation_el_type-{relation_number}")]]


def create_knowledge_element(number: int) -> gui.Frame:
    layout = [
        [gui.Text("TYP:", tooltip="Art des Wissens"),
         gui.DropDown(ELEMENT_TYPES, ELEMENT_TYPES[0], key=f"element-{number}-type")],
        [gui.Text("Name/ID:", tooltip="Die ID setzt sich aus dem Input und dem Typ zusammen"),
         gui.Input("", key=f"element-{number}-name", tooltip="Die ID setzt sich aus dem Input und dem Typ zusammen")],
        [gui.Text("Name/ID-Struktur-Element:", tooltip="Die ID des Strukturelements"),
         gui.Input("", key=f"element-{number}-structure-name",
                   tooltip="Die ID des Strukturelements")],
        [gui.Text("Inhalt:"), gui.Multiline("", key=f"element-{number}-content", size=(35, 3))],
        [gui.Frame("Relations",
                   create_new_relation(number, 1), key=f"Frame-{number}-relations")],
        [gui.Button("Weitere Relation", key=f"new-relation-{number}")]]
    return gui.Frame("", layout=layout, key=f"Frame-element-{number}")


def create_knowledge_window() -> gui.Window:
    structure_layout = create_structure_column_layout()
    layout = [[gui.Column([[gui.Frame("Elemente", [[create_knowledge_element(1)]], key="Frame-elements")]]),
               gui.Column([[gui.Frame("Struktur", structure_layout)]])],
              [gui.Button("Neues Element", key="new-element"), gui.Input("", key="output-name"),
               gui.Button("Speichern", key="save"),
               gui.Button("Neuer Wissenssatz", key="new-knowledge-set",
                          tooltip="Neues leeres Fenster, um neuen Wissenssatz zu erstellen.")]]
    return gui.Window("Neues Wissen", layout=[[gui.Column(layout=layout, size=(950, 300), expand_x=True, expand_y=True,
                                                          scrollable=True, vertical_scroll_only=True,
                                                          vertical_alignment="t")]],
                      resizable=True, auto_size_text=True)


def new_knowledge_file(values, window):
    # answer = gui.popup("Soll die aktuelle datei gespeichert werden?")
    window.disable()
    answer, _ = gui.Window('Neues Wissensset?',
                           [[gui.T('Soll das bestehende Wissen gespeichert werden?')],
                            [gui.Yes(s=10), gui.No(s=10), gui.Cancel(s=10)]],
                           disable_close=True).read(close=True)
    window.enable()
    window.bring_to_front()
    if answer == "Yes":
        save(values)  # can throw IDException
        window.close()
        gui.popup_ok("Datei wurde gespeichert!")
        window = create_knowledge_window()
        window.finalize()
    elif answer == "No":
        window.close()
        window = create_knowledge_window()
        window.finalize()
    return window


def on_win_closed(values, window):
    window.disable()
    answer, _ = gui.Window('Neues Wissensset?',
                           [[gui.T('Soll das bestehende Wissen gespeichert werden?')],
                            [gui.Yes(s=10), gui.No(s=10), gui.Cancel(s=10)]],
                           disable_close=True).read(close=True)
    if answer == "Yes":
        save(values)
        gui.popup_ok("Datei wurde gespeichert!")
    window.close()


def run_new_knowledge(window: gui.Window):
    event: str
    n = 1
    while True:
        event, values = window.read()
        if event == gui.WINDOW_CLOSED:
            return
        elif event == gui.WIN_X_EVENT:
            try:
                on_win_closed(values, window)
            except IdException:
                continue
            break
        elif re.match(r"new-relation-\d+", event):
            number = int(event.split('-')[2])
            frame: gui.Frame = window.find_element(f"Frame-{number}-relations")
            relation_number = len(frame.widget.children) + 1
            window.extend_layout(frame, create_new_relation(number, relation_number))
        elif event == "new-element":
            frame = window.find_element("Frame-elements")
            number = len(frame.widget.children)
            window.extend_layout(frame, [[create_knowledge_element(number + 1)]])
        elif event == "save":
            try:
                save(values)
            except IdException as e:
                print(e)
                continue
            window.disable()
            gui.popup_ok("Datei wurde gespeichert!")
            window.enable()
        elif event == "new-knowledge-set":
            try:
                window = new_knowledge_file(values, window)
            except IdException:
                continue
        elif re.match(r"add-[/_\w]*-child", event):
            add_structure_element(event, window)
        else:
            print("Unbekanntes Event! Abbruch!")
            window.close()
            break
        old_size = window.size
        n *= -1
        window.size = (old_size[0], old_size[1] + n)
    return
