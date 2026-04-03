from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MetricsSnapshot(BaseModel):
    current_rtt_ms: float = 0.0
    avg_rtt_ms: float = 0.0
    p95_rtt_ms: float = 0.0
    p99_rtt_ms: float = 0.0
    packet_loss_pct: float = 0.0
    jitter_ms: float = 0.0


class RuntimeState(BaseModel):
    updated_at: str
    components: dict[str, Literal["up", "down", "degraded", "active", "idle", "unknown", "running", "attached", "detached"]]
    active_testcase: str = ""
    active_scenario: str = ""
    active_slice: str = ""
    nr_profile: str = ""
    channel_profile: str = ""
    attach_state: str = "detached"
    ue_ip: str = ""
    metrics: MetricsSnapshot = Field(default_factory=MetricsSnapshot)
    recent_events: list[dict] = Field(default_factory=list)


class TestcaseState(BaseModel):
    name: str = ""
    scenario_class: str = ""
    expected_kpis: dict = Field(default_factory=dict)


class SliceState(BaseModel):
    name: str = ""
    sst: int = 1
    sd: str = ""
    dnn: str = ""
