# Copyright 2019 John Reese
# Licensed under the MIT license

import builtins
import logging
import re
import typing
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

from attr import astuple

from .types import Config, Line, Lines

log = logging.getLogger(__name__)
directive_re = re.compile(r"\s*..\s+(\w+)::\s+([^\n]+)")
callable_re = re.compile(r"\s*(\w+)(?:\(([^\)]*)\))?")
param_re = re.compile(r"\s*:(\w+)\s+(.+)\s+(\w+):")


def setup_logger(debug: bool = False):
    logging.addLevelName(logging.DEBUG, "DBG")
    logging.addLevelName(logging.INFO, "INF")
    logging.addLevelName(logging.WARNING, "WRN")
    logging.addLevelName(logging.ERROR, "ERR")
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(levelname)s %(message)s",
    )


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
            for lineno, content in enumerate(f, start=1):
                match = prefix_re.match(content)
                if match:
                    content = content[match.end() + 1 :]
                    dmatch = directive_re.match(content)
                    pmatch = param_re.match(content)

                    if dmatch:
                        kind, *extra = dmatch.groups()
                        lines.append(Line(source, lineno, kind, extra))
                    elif pmatch:
                        kind, *extra = pmatch.groups()
                        lines.append(Line(source, lineno, kind, extra))

        return lines

    def parse_dir(self, source_dir: Path) -> Dict[Path, Lines]:
        source_dir = source_dir.expanduser()
        docs: Dict[Path, Lines] = {}

        for path in source_dir.iterdir():
            if path.is_dir():
                docs.update(self.parse_dir(path))
            elif path.is_file():
                lines = self.parse_file(path)
                if lines:
                    docs[path] = lines

        return docs

    def organize(self, contents: Dict[Path, Lines]) -> Dict[str, Lines]:
        modules: Dict[str, Lines] = defaultdict(list)
        for _path, lines in contents.items():
            module: str = "builtins"
            for line in lines:
                if line.kind in ("module", "currentmodule"):
                    module = line.extra[0]
                if line.kind not in self.config.ignore_directives:
                    modules[module].append(line)
        for name in modules:
            modules[name] = list(
                sorted(modules[name], key=lambda l: 1 if l.kind == "module" else 2)
            )
        return modules

    def render(self, line: Line, kind: str = None, **kwargs: str) -> str:
        if kind is None:
            kind = line.kind
        tpl = getattr(self.config, f"{kind}_template")
        return tpl.format(
            source=line.source,
            lineno=line.lineno,
            kind=kind,
            extra=line.extra,
            **kwargs,
        )

    def gen_stub(self, dest: Path, lines: Lines) -> None:
        log.debug("generating stub %s", dest)
        config = self.config
        content: List[str] = []
        type_names: Set[str] = set()
        count = len(lines)
        idx = 0
        while idx < count:
            line = lines[idx]
            path, lineno, kind, extra = astuple(line)
            if kind in ("module",):
                name, *_ = extra
                content.append(self.render(line, name=name))

            elif kind in ("class", "method", "function"):
                call, = extra
                match = callable_re.match(call)
                if not match:
                    idx += 1
                    log.error(
                        "%s:%d: failed to parse %s directive: %s",
                        path,
                        lineno,
                        kind,
                        call,
                    )
                    continue

                name, param_str = match.groups()
                if param_str is None:
                    content.append(
                        self.render(line, name=name, args="", ret_type="Any")
                    )
                    idx += 1
                    continue

                params = [
                    [n.strip(" []"), "Any", v.strip(" []")]
                    for p in param_str.split(",")
                    for n, _, v in [p.partition("=")]
                ]

                while idx + 1 < count and lines[idx + 1].kind == "param":
                    idx += 1
                    p_type, p_name = lines[idx].extra
                    for pidx, (n, _, v) in enumerate(params):
                        if n == p_name:
                            params[pidx][1] = p_type
                            break

                type_names.update(t for _, t, _ in params)
                args = ", ".join(
                    self.render(
                        line,
                        kind="arg",
                        name=n,
                        arg_type=t,
                        equal=" = " if v else "",
                        value=v,
                    )
                    for n, t, v in params
                )
                content.append(self.render(line, name=name, args=args, ret_type="Any"))
            elif kind in ("attribute", "data"):
                name, *_ = extra
                attr_type = "Any"
                type_names.add(attr_type)
                content.append(
                    self.render(line, kind="attribute", name=name, attr_type=attr_type)
                )
            elif kind in ("currentmodule", "note", "warning"):
                pass  # ignore these directives
            else:
                log.warning(
                    "%s:%d: unmatched %s directive: %s", path, lineno, kind, extra
                )
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
