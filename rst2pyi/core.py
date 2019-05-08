# Copyright 2019 John Reese
# Licensed under the MIT license

import builtins
import re
import typing

from collections import defaultdict
from docutils.parsers.rst import Parser
from docutils.utils import new_document
from docutils.core import publish_doctree
from pathlib import Path
from typing import Dict, Optional, List, Any, Set

from .config import Config
from .types import Document, Lines

directive_re = re.compile(r"\s*..\s+(\w+)::\s+([^\n]+)")
callable_re = re.compile(r"\s*(\w+)(?:\(([^\)]*)\))?")
param_re = re.compile(r"\s*:(\w+)\s+(.+)\s+(\w+):")


class Converter:
    def __init__(self, source_dir: Path, dest_dir: Path, **kwargs: Any):
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.config = Config(**kwargs)

        self.prefix_re = re.compile(self.config.line_prefix)

    def parse_file(self, source: Path) -> Lines:
        lines = []
        prefix_re = self.prefix_re
        with open(source, "r") as f:
            for line in f:
                match = prefix_re.match(line)
                if match:
                    line = line[match.end() + 1 :]
                    dmatch = directive_re.match(line)
                    pmatch = param_re.match(line)

                    if dmatch:
                        lines.append(dmatch.groups())
                    elif pmatch:
                        lines.append(pmatch.groups())

        return lines

    def parse_dir(self, source_dir: Path) -> Dict[Path, Lines]:
        source_dir = source_dir.expanduser().resolve()
        docs: Dict[Path, Lines] = {}

        for path in source_dir.iterdir():
            if path.is_dir():
                docs.update(self.parse_dir(path))
            elif path.is_file():
                doc = self.parse_file(path)
                if doc:
                    docs[path] = doc

        return docs

    def organize(self, contents: Dict[Path, Lines]) -> Dict[str, Lines]:
        modules: Dict[str, lines] = defaultdict(list)
        for path, lines in contents.items():
            module: str = "builtins"
            for line in lines:
                kind, *extra = line
                if kind in ("module", "currentmodule"):
                    module = extra[0]
                if kind not in self.config.ignore_directives:
                    modules[module].append(line)
        for name in modules:
            modules[name] = list(
                sorted(modules[name], key=lambda l: 1 if l[0] == "module" else 2)
            )
        return modules

    def gen_stub(self, dest: Path, lines: Lines) -> None:
        print(f"{dest}")
        config = self.config
        content: List[str] = []
        type_names: Set[str] = set()
        count = len(lines)
        idx = 0
        while idx < count:
            line = lines[idx]
            kind, *extra = lines[idx]
            if kind in ("modules"):
                name, *_ = extra
                content.append(config.module_template.format(name=name))

            elif kind in ("class", "method", "function"):
                call, = extra
                match = callable_re.match(call)
                if not match:
                    idx += 1
                    continue  # TODO: throw a warning or something?

                name, params = match.groups()
                if params is None:
                    content.append(
                        getattr(config, f"{kind}_template").format(
                            name=name, args="", ret_type=""
                        )
                    )
                    idx += 1
                    continue

                params = [
                    [n.strip(" []"), "Any", v.strip(" []")]
                    for p in params.split(",")
                    for n, _, v in [p.partition("=")]
                ]

                while idx + 1 < count and lines[idx + 1][0] == "param":
                    idx += 1
                    _, p_type, p_name = lines[idx]
                    for pidx, (n, t, v) in enumerate(params):
                        if n == p_name:
                            params[pidx][1] = p_type
                            break

                type_names.update(t for _, t, _ in params)
                args = ", ".join(
                    config.arg_template.format(
                        name=n, arg_type=t, equal=" = " if v else "", value=v
                    )
                    for n, t, v in params
                )
                content.append(
                    getattr(config, f"{kind}_template").format(
                        name=name, args=args, ret_type="Any"
                    )
                )
            elif kind in ("attribute", "data"):
                name, *_ = extra
                attr_type = "Any"
                type_names.add(attr_type)
                content.append(
                    config.attribute_template.format(name=name, attr_type=attr_type)
                )
            elif kind in ("currentmodule", "note", "warning"):
                pass  # ignore these directives
            else:
                print(kind, extra)
            idx += 1

        content.append("")

        imports: Set[str] = set()
        for name in type_names:
            name, _, _ = name.partition(".")
            if hasattr(builtins, name):
                continue
            elif hasattr(typing, name):
                imports.add(config.from_template.format(module="typing", name=name))
            else:
                imports.add(config.import_template.format(name=name))

        content[:0] = list(
            sorted(imports, key=lambda l: f"z{l}" if l.startswith("from") else l)
        )

        with open(dest, "w") as f:
            f.write("\n".join(content))

    def gen_stubs(self) -> None:
        content = self.parse_dir(self.source_dir)
        modules = self.organize(content)
        for module, data in modules.items():
            self.dest_dir.mkdir(parents=True, exist_ok=True)
            dest = self.dest_dir / f"{module}.pyi"
            self.gen_stub(dest, data)

