from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich import print as rprint


def build_tree(data):
    tree = Tree("Data")
    for key, value in data.items():
        if isinstance(value, dict):
            subtree = build_tree(value)
            tree.add(key)
            tree.add(subtree)
        elif isinstance(value, str) and "/" in value:
            with open(value, "r") as f:
                contents = f.read()
            panel = Panel(contents, title=key, border_style="green")
            tree.add(panel)
        else:
            tree.add(f"{key}: {value}")
    return tree


data = {
    "dir1": {
        "file1": "/tmp/workspaces/config.xml",
        "file2": "/tmp/workspaces/PATHONE/sample.json",
        "file3": "/tmp/workspaces/PATHONE/sample.xml"
    },
    "dir2": {
        "file3": "/tmp/workspaces/config.xml",
        "file4": "not a file path"
    },
    "file5": "/tmp/workspaces/config.xml",
    "value1": 123
}

tree = build_tree(data)
console = Console()
# rprint(tree)
console.print(tree)
