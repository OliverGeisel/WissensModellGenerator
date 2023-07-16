import re

import PySimpleGUI as gui

from core import save_as_file, add_empty_source, IdException, collect_structure


def create_new_structure_child(structure_frame: gui.Frame):
    key = structure_frame.key.removesuffix("-children").removeprefix("structure-")
    element_num = len(structure_frame.widget.children)
    new_key = key + f"/{element_num}"
    frame = gui.Frame("", [[gui.Text("Name:"), gui.Input(key=f"structure-{new_key}-id")],
                           [gui.Column([[]], key=f"structure-{new_key}-children")],
                           [gui.Button("Neues Kindelement", key=f"add-{new_key}-child")]],
                      key=f"structure-{new_key}-structure-frame")
    back = [[frame]]
    return back


def add_structure_element(event: str, window: gui.Window):
    key = event.removeprefix("add-").removesuffix("-child")
    structure_frame = window.find_element(f"structure-{key}-children")
    window.extend_layout(structure_frame, create_new_structure_child(structure_frame))


def create_structure_column_layout():
    back = [[gui.Text("Area of Knowledge: "), gui.Input(key="structure-area-of-knowledge")],
            [gui.Frame("Area of Knwoledge Kindelemente", [[gui.Column([[]], key="structure-_root-children")]],
                       key="structure-_root-structure-frame")],
            [gui.Column([[gui.Button("Neues Kindelement", key="add-_root-child")]])]
            ]
    return back


def create_structure_window() -> gui.Window:
    structure_layout = create_structure_column_layout()
    layout = [[gui.Column([[gui.Frame("Struktur", structure_layout)]])],
              [gui.Button("Neues Element", key="new-element"), gui.Input("", key="output-name"),
               gui.Button("Speichern", key="save"),
               gui.Button("Neuer Wissenssatz", key="new-knowledge-set",
                          tooltip="Neues leeres Fenster um neuen Wissenssatz zu erstellen.")]]
    return gui.Window("Neue WissenElemente/Struktur",
                      layout=[[gui.Column(layout=layout, size=(650, 300), expand_x=True, expand_y=True,
                                          scrollable=True, vertical_scroll_only=True,
                                          vertical_alignment="t")]],
                      resizable=True, auto_size_text=True)


def save(values: dict[str, str]):
    knowledge_model = {"knowledge": list()}
    add_empty_source(knowledge_model)
    collect_structure(knowledge_model, values)
    save_as_file(knowledge_model, values["output-name"])


def run_new_structure(window: gui.Window):
    event: str
    n = 1
    while True:
        event, values = window.read()
        if event == gui.WINDOW_CLOSED:
            return
        elif event == gui.WIN_X_EVENT:
            window.disable()
            answer, _ = gui.Window('Neues Wissensset?',
                                   [[gui.T('Soll das bestehende Wissen gespeichert werden?')],
                                    [gui.Yes(s=10), gui.No(s=10), gui.Cancel(s=10)]],
                                   disable_close=True).read(close=True)
            if answer == "Yes":
                try:
                    save(values)
                except IdException:
                    window.enable()
                    continue
                gui.popup_ok("Datei wurde gespeichert!")
            window.close()
            break
        elif event == "save":
            try:
                save(values)
            except IdException:
                continue
            window.disable()
            gui.popup_ok("Datei wurde gespeichert!")
            window.enable()
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
