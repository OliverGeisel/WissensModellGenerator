import json
import pathlib
import re

import PySimpleGUI as gui


class IdException(Exception):
    """
    Exception, that the id is not valid
    """
    pass


def save_as_file(model: dict, output_name: str, base_file_name="file"):
    file_str = json.dumps(model)
    path = pathlib.Path("./files/config.json")
    with open(path, "r") as config:
        output_path_base = pathlib.Path(json.loads(config.read())["path-to-output"])
    output_file_path = output_path_base.joinpath(f"{output_name}.json")
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


def parse_relations(keys: list, values: dict) -> list:
    back = []
    count = 0
    while count + 2 < len(keys):
        if "" not in [values[keys[count]], values[keys[count + 1]]]:
            new_relation = {"relation_id": values[keys[count + 1]] + "-" + values[keys[count + 2]].upper(),
                            "relation_type": values[keys[count]]
                            }
            back.append(new_relation)
        count += 3
    return back


def parse_structure(id_keys: list, parent: dict, values: dict) -> dict:
    for key in id_keys:
        key_without_suffix = key.removesuffix("-id")
        if re.match(r"\d+-id", key):
            new_last_element = {"key": parent["key"] + "/" + key_without_suffix,
                                "name": values[f"structure-{parent['key']}/{key}"],
                                "children": list()}
            parent["children"].append(new_last_element)
            new_keys = [child_key.removeprefix(key_without_suffix + "/") for child_key in id_keys if
                        child_key.startswith(key_without_suffix + "/")]
            parse_structure(new_keys, new_last_element, values)
    return parent


def collect_structure(knowledge_model, values):
    structure_keys = [key.removeprefix("structure-") for key in values if key.startswith("structure-")]
    id_keys = [key.removeprefix("_root/") for key in structure_keys if key.startswith("_root/")]
    area_of_knowledge = values['structure-area-of-knowledge']
    structure = {"name": area_of_knowledge, "key": "_root", "children": list()}
    parse_structure(id_keys, structure, values)
    knowledge_model["structure"] = structure


def create_example_element(keys, values) -> dict:
    content = values[keys[6]]
    if not content.startswith("content:"):
        content = "content:" + content
    if content == "":
        content = "content:;"
    endung = values[keys[5]]
    bild = f";image:{values[keys[3]]}.{endung}" if values[keys[3]] != "" else ";image:;"
    titel = f";title:{values[keys[4]]}" if values[keys[4]] != "" else "title:;"
    content += bild + titel
    return {"type": "EXAMPLE",
            "id": f"{values[keys[1]]}-EXAMPLE",
            "structure": values[keys[2]],
            "content": content,
            "relations":
                parse_relations(keys[7:], values)
            }
    pass


def collect_elements(elements, values):
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
            raise IdException
        type_name = values[keys[0]].upper()
        if type_name == "EXAMPLE_OWN":
            element = create_example_element(keys, values)
        else:
            element = {"type": type_name,
                   "id": f"{values[keys[1]]}-{type_name}",
                   "structure": values[keys[2]],
                   "content": values[keys[3]] if values[keys[3]] != "" else
                   (values[keys[1]] if type_name != "Term" else ""),
                   "relations":
                       parse_relations(keys[4:], values)
                   }
        elements.append(element)


def add_empty_source(knowledge_model):
    knowledge_model["sources"] = [{
        "type": "UNKNOWN_SOURCE",
        "id": "Unbekannt-UNKNOWN_SOURCE",
        "name": "",
        "content": ""
    }]


def save(values: dict[str, str]):
    knowledge_model = dict()
    elements = []
    knowledge_model["knowledge"] = elements

    collect_elements(elements, values)
    collect_structure(knowledge_model, values)
    add_empty_source(knowledge_model)

    save_as_file(knowledge_model, values["output-name"])
