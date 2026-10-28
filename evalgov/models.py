from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, strict=True)


class Document(StrictModel):
    id: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=10000)


class Expected(StrictModel):
    answer_terms: list[str] = Field(default_factory=list)
    forbidden_terms: list[str] = Field(default_factory=list)
    refused: bool = False
    required_citations: list[str] = Field(default_factory=list)
    allowed_citations: list[str] = Field(default_factory=list)
    # Tool arguments must exactly match one of these approved calls. No wildcard execution.
    allowed_calls: list[dict[str, Any]] = Field(default_factory=list)
    required_calls: list[dict[str, Any]] = Field(default_factory=list)
    allow_pii: bool = False


class Case(StrictModel):
    id: str = Field(min_length=1, max_length=100)
    category: Literal["grounding", "refusal", "privacy", "injection", "tools", "access"]
    prompt: str = Field(min_length=1, max_length=10000)
    documents: list[Document] = Field(default_factory=list, max_length=30)
    expected: Expected


class ToolCall(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    arguments: dict[str, Any]


class Usage(StrictModel):
    input_tokens: int = Field(ge=0, le=10000000, strict=True)
    output_tokens: int = Field(ge=0, le=10000000, strict=True)


class Answer(StrictModel):
    answer: str = Field(max_length=50000)
    citations: list[str] = Field(max_length=100)
    refused: bool
    tool_calls: list[ToolCall] = Field(max_length=20)
    usage: Usage


class Thresholds(StrictModel):
    min_pass_rate: float = Field(default=1, ge=0, le=1)
    max_latency_ms: float = Field(default=10000, gt=0)
    max_cost_usd: float = Field(default=0.05, ge=0)
    max_regression: float = Field(default=0, ge=0, le=1)
    input_per_million: float = Field(default=1, ge=0)
    output_per_million: float = Field(default=4, ge=0)


class PolicyRequest(StrictModel):
    use_case: str = Field(min_length=3, max_length=200)
    personal_data: bool
    special_category_data: bool = False
    externally_visible_action: bool
    financial_posting: bool = False
    approved_data_source: bool
    retention_days: int = Field(ge=1, le=3650)
    owner: str = Field(min_length=2, max_length=100)
