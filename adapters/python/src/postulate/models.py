from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Scenario(BaseModel):
    name: str = Field(min_length=1)
    given: dict[str, Any] = Field(default_factory=dict)
    when: dict[str, Any] = Field(default_factory=dict)
    then: dict[str, Any] = Field(default_factory=dict)


class Contract(BaseModel):
    preconditions: list[str] = Field(min_length=1)
    postconditions: list[str] = Field(min_length=1)
    failure_cases: list[str] = Field(default_factory=list)


RiskLevel = Literal["low", "medium", "high", "critical"]


class PostulateSpec(BaseModel):
    feature: str = Field(min_length=1)
    owner: str | None = None
    risk: RiskLevel = "medium"
    contract: Contract
    invariants: list[str] = Field(default_factory=list)
    bdd: list[Scenario] = Field(min_length=1)
    policies: list[str] = Field(default_factory=list)
    test_mapping: dict[str, str] = Field(default_factory=dict)
    correctness_argument: str | None = None
