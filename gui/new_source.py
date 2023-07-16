import PySimpleGUI as gui

from core import save_as_file
from gui.new_knowledge import IdException

MEDIA_TYPES = ("Internal_Media", "Resolvable_Reference", "Not_Resolvable_Reference", "Unknown_Source")


def new_source_element(number: int) -> gui.Frame:
    layout = [
        [gui.Text("TYP:"),
         gui.DropDown(MEDIA_TYPES,
                      MEDIA_TYPES[0], key=f"source-{number}-type")],
        [gui.Text("Name/ID:", tooltip="Die ID setzt sich aus dem Input und dem Typ zusammen. Muss einzigartig sein!"),
         gui.Input("", key=f"source-{number}-id",
                   tooltip="Die ID setzt sich aus dem Input und dem Typ zusammen. Muss einzigartig sein!")],
        [gui.Text("Bezeichnung:", tooltip="Die Bezeichnung kann für mehrere Quellen gleich sein."),
         gui.Input("", key=f"source-{number}-name", tooltip="Die Bezeichnung kann für mehrere Quellen gleich sein.")],
        [gui.Text("Inhalt:"), gui.Multiline("", key=f"source-{number}-content", size=(35, 3))],
    ]
    return gui.Frame("", layout=layout, key=f"Frame-source-{number}")


def create_source_window() -> gui.Window:
    layout = [[gui.Frame("Quellen", [[new_source_element(1)]], key="Frame-sources")],
              [gui.Button("Neue Quelle", key="new-source"), gui.Input("", key="output-name"),
               gui.Button("Speichern", key="save"),
               gui.Button("Neue Wissensquellen", key="new-knowledge-set",
                          tooltip="Neues leeres Fenster, um neuen Quellensatz zu erstellen.")]]
    return gui.Window("Neue Wissensquellen",
                      layout=[[gui.Column(layout=layout, size=(650, 300), expand_x=True, expand_y=True,
                                          scrollable=True, vertical_scroll_only=True,
                                          vertical_alignment="t")]],
                      resizable=True, auto_size_text=True)


def save(values: dict[str, str]):
    knowledge_model = {"knowledge": list(), "structure": dict()}
    collect_source(knowledge_model, values)
    save_as_file(knowledge_model, values["output-name"])


def collect_source(knowledge_model: dict, values: dict):
    sources = []
    elem_key = [key for key in values if key.startswith("source")]
    source_groups = dict()
    for key in elem_key:
        number = key.split("-")[1]
        if number not in source_groups:
            source_groups[number] = list()
        source_groups[number].append(key)
    for group, keys in source_groups.items():
        if values[keys[1]] == "":
            gui.popup_error(f"Quelle {group} hat keine ID. Bitte angeben", title="Fehlende ID")
            raise IdException
        source = {"type": values[keys[0]].upper(),
                  "id": f"{values[keys[1]]}-{values[keys[0]].upper()}",
                  "name": values[keys[2]],
                  "content": values[keys[3]]}
        sources.append(source)
    knowledge_model["sources"] = sources


def run_new_source(window: gui.Window):
    event: str
    n = 1
    while True:
        event, values = window.read()
        if event == gui.WIN_CLOSED:
            break
        if event in [gui.WIN_CLOSED]:
            window.disable()
            answer, _ = gui.Window('Neues Quellenset?',
                                   [[gui.T('Sollen die bestehenden Quellen gespeichert werden?')],
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
            elif answer == "No":
                window.close()
                break
            window.enable()
        elif event == "new-source":
            frame = window.find_element("Frame-sources")
            number = len(frame.widget.children)
            window.extend_layout(frame, [[new_source_element(number + 1)]])
        elif event == "save":
            try:
                save(values)
            except IdException:
                continue
            window.disable()
            gui.popup_ok("Datei wurde gespeichert!")
            window.enable()
        else:
            print("Unbekanntes Event! Abbruch!")
            window.close()
            break
        old_size = window.size
        n *= -1
        window.size = (old_size[0], old_size[1] + n)
    return
