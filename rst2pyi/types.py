# Copyright 2019 John Reese
# Licensed under the MIT license

from pathlib import Path
from typing import List, Sequence, Set

from attr import dataclass


@dataclass
class Config:
    # regex to match lines - unmatched lines will not be converted
    line_prefix: str = r"\s*//\|"
    ignore_directives: Set[str] = {"warning", "note", "currentmodule"}

    module_template: str = '\n"""\n{name}\n"""\n'
    class_template: str = (
        "\n# {source}:{lineno}\nclass {name}:\n    def __init__(self, {args}): ..."
    )
    method_template: str = "    def {name}(self, {args}) -> {ret_type}: ..."
    attribute_template: str = "    {name}: {attr_type} = ..."
    function_template: str = (
        "\n# {source}:{lineno}\ndef {name}({args}) -> {ret_type}: ..."
    )
    arg_template: str = "{name}: {arg_type}{equal}{value}"
    import_template: str = "import {name}"
    from_template: str = "from {module} import {name}"


@dataclass
class Line:
    source: Path
    lineno: int
    kind: str
    extra: Sequence[str]


Lines = List[Line]
