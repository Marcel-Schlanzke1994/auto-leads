from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

AnalysisStatus = Literal["success", "skipped", "failed", "unavailable"]
FieldClass = Literal[
    "name", "email", "phone", "message", "company", "subject", "consent", "unknown"
]


@dataclass(slots=True)
class ContactFormField:
    name: str
    input_type: str
    label: str
    selector: str | None = None
    classified_as: FieldClass = "unknown"


@dataclass(slots=True)
class ContactFormSummary:
    action: str | None
    method: str | None
    fields: list[ContactFormField] = field(default_factory=list)
    has_submit_button: bool = False
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BrowserAnalysisResult:
    url: str
    status: AnalysisStatus
    contact_page_url: str | None = None
    forms_found: list[ContactFormSummary] = field(default_factory=list)
    fields: list[ContactFormField] = field(default_factory=list)
    screenshot_path: str | None = None
    recommendations: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
