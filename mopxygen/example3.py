

import enum
from typing import List
from pathlib import Path
from xml.etree import ElementTree as et
from rich.tree import Tree
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.console import Group, Console
from dataclasses import dataclass

# ////////////////////////////////////////////////////////////////////// New


class SchemaType(enum.Enum):
    NodeConfig = 0,
    TestCase = 1,
    Archive = 2,
    Fault = 3


@dataclass
class ConfigFile:
    schema_type: SchemaType
    filename: Path
    sub_files: list  # List[ConfigFile]


@dataclass
class Workspace:
    name: str
    # type: str
    path: Path


def generate_summary():
    sample_data = {}
    with open(" a ple.json", "r") as f:
        sample_aa = json.loads(f.read())

        summary = Table(row_styles=["", "dim"])
    summary.add_column("Date Modified", style="cyan", no_wrap=True)
    summary.add_column("Filename", style="magenta")
    summary.add_column("Health", justify="right", style="green")


def show_heirarchy(data: dict):
    """ Given a dict of data
    {
        "filename": {
            "schema_type": "config-type1"
            "filenames inside": {
            }
        }
    }
    """
    pass


if __name__ == "__main__":
    # Integration stuff
    # Make some workspaces.
    # workspaces: List[Workspace] = [
    #     Workspace("PATHONE", Path("/tmp/workspaces/PATHONE")),
    #     Workspace("PATHTWO", Path("/tmp/workspaces/PATHTWO")),
    #     Workspace("PATHTHREE", Path("/tmp/workspaces/PATHTHREE")),
    # ]

    # for space in workspaces:
    #     space.path.mkdir(parents=True, exist_ok=True)

    tree = et.parse("/tmp/workspaces/config.xml")
    root = tree.getroot()
    spaces = root[0][0]

    workspaces: List[Workspace] = []
    for workspace in spaces:
        workspaces.append(
            Workspace(name=workspace.attrib["alias"], path=workspace.text))
        # Actual code

    def build_tree(workspaces: List[Workspace]):
        root_file_json = {}

        workspace_files = []
        for space in workspaces:
            # TODO: if type not archive
            workspace_files += list(space.path.glob("*.xml"))

        new_workspaces = []
        # for file in workspace_files:
        #     if file.type

        return workspaces

    print(workspaces)
    # tree = build_tree(workspaces)
