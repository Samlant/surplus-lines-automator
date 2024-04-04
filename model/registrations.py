from dataclasses import dataclass, InitVar

from helper import open_config


FORM_PREFIX = "Template_"


@dataclass(kw_only=True)
class Producer:
    name: str
    pname: str
    paddress: str
    city_st_zip: str

    def values(self) -> tuple[str]:
        return (
            self.name,
            self.pname,
            self.paddress,
            self.city_st_zip,
        )


def process_save(row_data) -> bool:
    "Clear's exisiting quoteforms that are saved in the config file,  then saves all rows within treeview into the config file."
    config = open_config()
    config = _remove_all_sections(config)
    _add_treeview_data_into_conf(config, row_data)
    return True


def process_retrieval() -> list[Producer]:
    config = open_config()
    producer_names = __get_all_names_from_conf(config)
    templates: list[Producer] = []
    for name in producer_names:
        section = config.get_section(name)
        options = section.items()
        form = Producer(
            name=name,
            pname=options[0][1].value,
            paddress=options[1][1].value,
            city_st_zip=options[2][1].value,
        )
        templates.append(form)
    return templates


def _remove_all_sections(config):
    "Removes all existing quoteforms within config to start with a clean slate."
    names = __get_all_names_from_conf(config)
    for name in names:
        config.remove_section(name)
    config.update_file()
    return config


def __get_all_names_from_conf(config) -> list[str]:
    "Retrieves all names of quoteforms from the config file."
    return [y for y in config.sections() if FORM_PREFIX in y]


def _add_treeview_data_into_conf(config, row_data):
    "Adds all entries in treeview into the config file."
    for row in row_data:
        config["surplus lines"].add_before.section(row[0]).space(1)
        config[row[0]]["pname"] = row[1]
        config[row[0]]["paddress"] = row[2]
        config[row[0]]["city_st_zip"] = row[3]
        config.update_file()


def standardize_name(name: str) -> str:
    "Assigns a prefix to identify all quoteforms properly within the config file."
    return f"{FORM_PREFIX}{name}"


def validate_name(existing_names: list[str], name: str):
    "Ensures a duplicate name is not assigned."
    if name in existing_names:
        return False
    else:
        return True
