from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RunContext:
    tool_name: str
    input_path: Path | None = None
    output_path: Path | None = None
    report_path: Path | None = None
    log_path: Path | None = None
    genome_build: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "input_path": str(self.input_path) if self.input_path else None,
            "output_path": str(self.output_path) if self.output_path else None,
            "report_path": str(self.report_path) if self.report_path else None,
            "log_path": str(self.log_path) if self.log_path else None,
            "genome_build": self.genome_build,
            "metadata": self.metadata,
        }
