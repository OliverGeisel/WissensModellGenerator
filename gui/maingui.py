import json
import pathlib

import PySimpleGUI as gui


def create_main() -> gui.Window:
    layout = [[gui.Text("Wähle aus!")], [gui.Button("Einstellungen", key="settings")], [gui.Button("Neus Wissen")]]
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


def run_main(window: gui.Window):
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
    window.close()
