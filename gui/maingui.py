import json
import pathlib
from typing import Union

import PySimpleGUI as gui

from .new_knowlege import create_knowledge_window
from .new_source import create_source_window
from .new_structure import create_structure_window


def create_main() -> gui.Window:
    layout = [[gui.Text("Wähle aus!")],
              [gui.Button("Neues Wissen", key="new-knowledge")],
              [gui.Button("Neue Struktur", key="new-structure")],
              [gui.Button("Neue Wissensquelle", key="new-source")],
              [gui.HSep()],
              [gui.Button("Einstellungen", key="settings")]]
    return gui.Window("Wissensmodell Generator", layout)


def create_setting_window() -> gui.Window:
    path = pathlib.Path(__file__).absolute().parent.parent.joinpath("files/config.json")
    with open(path) as setting_file:
        settings = json.load(setting_file)
    layout = [[gui.Text("Speicherort der Files:"), gui.Input(f"{settings['path-to-output']}", key="path-to-output")],
              [gui.Button("Speichern", key="save")]]
    return gui.Window("Einstellungen", layout)


def save_settings(values: dict[str, str]):
    settings = json.dumps(values)
    path = pathlib.Path(__file__).absolute().parent.parent.joinpath("files/config.json")
    with open(path, "w") as setting_file:
        setting_file.write(settings)


def run_setting_window(window: gui.Window):
    while True:
        event, values = window.read()
        if event in [gui.WIN_X_EVENT, gui.WIN_CLOSED]:
            break
        if event == "save":
            save_settings(values)


def run_main(window: gui.Window) -> tuple[str, Union[gui.Window, None]]:
    while True:
        event, values = window.read()
        if event in [gui.WIN_X_EVENT, gui.WIN_CLOSED]:
            break
        if event == "settings":
            setting_window = create_setting_window()
            window.disable()
            run_setting_window(setting_window)
            window.enable()
            window.force_focus()
            setting_window.close()
        if event == "new-knowledge":
            window.close()
            return event, create_knowledge_window()
        if event == "new-structure":
            window.close()
            return event, create_structure_window()
        if event == "new-source":
            window.close()
            return event, create_source_window()
    window.close()
    return "END", None
