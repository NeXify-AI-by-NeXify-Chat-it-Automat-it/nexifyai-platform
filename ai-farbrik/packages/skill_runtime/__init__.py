"""
NeXifyAI — Skill Manifest System (Package: skill-runtime)

NOT: loose Skill markdown files
BUT:  typed governed skill definitions with manifest, risk, compensation

Each skill MUST declare:
  - capabilities required
  - risk classification
  - input/output schema
  - compensation action
  - observability contract

This is the next evolution beyond Paperclip skills.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import yaml
import json


# ═══════════════════════════════════════════════════
# SKILL MANIFEST
# ═══════════════════════════════════════════════════

class SkillRisk(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SkillStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"

@dataclass
class SkillCapability:
    """A capability token required by a skill."""
    name: str                              # e.g., "github.write"
    scope: str = ""                        # e.g., "repo:nexifyai-dev/*"
    expiry: str = ""                       # e.g., "1h", "session", "permanent"

@dataclass
class SkillInput:
    """Typed input parameter for a skill."""
    name: str
    type: str                              # "string", "integer", "boolean", "object", "array"
    required: bool = True
    description: str = ""
    default: Any = None

@dataclass
class SkillOutput:
    """Typed output for a skill."""
    name: str
    type: str
    description: str = ""

@dataclass
class SkillCompensation:
    """Compensating action for this skill."""
    action: str                            # e.g., "github.close_issue"
    description: str = ""
    automatic: bool = False                # Can it run automatically?
    requires_approval: bool = True

@dataclass
class SkillObservability:
    """Observability contract for a skill."""
    emits_events: bool = True
    log_level: str = "info"                # "debug", "info", "warn", "error"
    metrics: List[str] = field(default_factory=lambda: ["latency_ms", "success_rate"])
    tracing: bool = True

@dataclass
class SkillManifest:
    """
    Governed skill definition.

    Example YAML:
        skill_id: github.create_issue
        version: 1.0.0
        capabilities:
          - name: github.write
            scope: repo:nexifyai-dev/*
        risk:
          level: MEDIUM
          blast_radius: 1
        compensation:
          action: github.close_issue
          automatic: true
    """
    skill_id: str                          # e.g., "github.create_issue"
    version: str = "1.0.0"
    description: str = ""
    status: SkillStatus = SkillStatus.ACTIVE

    # Capabilities
    capabilities: List[SkillCapability] = field(default_factory=list)

    # Risk
    risk_level: SkillRisk = SkillRisk.LOW
    blast_radius: int = 1
    requires_approval: bool = False

    # I/O
    inputs: List[SkillInput] = field(default_factory=list)
    outputs: List[SkillOutput] = field(default_factory=list)

    # Compensation
    compensation: Optional[SkillCompensation] = None

    # Observability
    observability: SkillObservability = field(default_factory=SkillObservability)

    # Metadata
    connector: str = ""                    # "github", "vercel", "supabase", "browser", "slack"
    docs_url: str = ""
    tags: List[str] = field(default_factory=list)

    def to_yaml(self) -> str:
        """Serialize to YAML."""
        return yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True)

    def to_dict(self) -> Dict[str, Any]:
        """Serializable representation."""
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "description": self.description,
            "status": self.status.value,
            "capabilities": [
                {"name": c.name, "scope": c.scope, "expiry": c.expiry}
                for c in self.capabilities
            ],
            "risk": {
                "level": self.risk_level.value,
                "blast_radius": self.blast_radius,
                "requires_approval": self.requires_approval,
            },
            "inputs": [
                {"name": i.name, "type": i.type, "required": i.required,
                 "description": i.description}
                for i in self.inputs
            ],
            "outputs": [
                {"name": o.name, "type": o.type, "description": o.description}
                for o in self.outputs
            ],
            "compensation": {
                "action": self.compensation.action,
                "description": self.compensation.description,
                "automatic": self.compensation.automatic,
            } if self.compensation else None,
            "observability": {
                "emits_events": self.observability.emits_events,
                "log_level": self.observability.log_level,
                "metrics": self.observability.metrics,
            },
            "connector": self.connector,
            "tags": self.tags,
        }

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "SkillManifest":
        """Parse from YAML."""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillManifest":
        """Parse from dict."""
        risk = data.get("risk", {})
        comp = data.get("compensation", {})
        obs = data.get("observability", {})

        return cls(
            skill_id=data["skill_id"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            status=SkillStatus(data.get("status", "active")),
            capabilities=[
                SkillCapability(name=c["name"], scope=c.get("scope", ""),
                               expiry=c.get("expiry", ""))
                for c in data.get("capabilities", [])
            ],
            risk_level=SkillRisk(risk.get("level", "LOW")),
            blast_radius=risk.get("blast_radius", 1),
            requires_approval=risk.get("requires_approval", False),
            inputs=[
                SkillInput(name=i["name"], type=i["type"],
                          required=i.get("required", True),
                          description=i.get("description", ""))
                for i in data.get("inputs", [])
            ],
            outputs=[
                SkillOutput(name=o["name"], type=o["type"],
                           description=o.get("description", ""))
                for o in data.get("outputs", [])
            ],
            compensation=SkillCompensation(
                action=comp["action"],
                description=comp.get("description", ""),
                automatic=comp.get("automatic", False),
                requires_approval=comp.get("requires_approval", True),
            ) if comp else None,
            observability=SkillObservability(
                emits_events=obs.get("emits_events", True),
                log_level=obs.get("log_level", "info"),
                metrics=obs.get("metrics", ["latency_ms"]),
            ),
            connector=data.get("connector", ""),
            tags=data.get("tags", []),
        )


# ═══════════════════════════════════════════════════
# STANDARD SKILL MANIFESTS
# ═══════════════════════════════════════════════════

STANDARD_SKILLS = {
    "github.create_issue": SkillManifest(
        skill_id="github.create_issue",
        version="1.0.0",
        description="Create a GitHub issue in the NeXifyAI repository",
        capabilities=[SkillCapability(name="github.write", scope="repo:nexifyai-dev/*")],
        risk_level=SkillRisk.MEDIUM,
        blast_radius=1,
        inputs=[
            SkillInput("title", "string", True, "Issue title"),
            SkillInput("body", "string", False, "Issue body (markdown)"),
        ],
        outputs=[SkillOutput("issue_number", "integer", "Created issue number")],
        compensation=SkillCompensation("github.close_issue", "Close the created issue", True),
        connector="github",
        tags=["github", "write", "issue"],
    ),
    "github.create_pr": SkillManifest(
        skill_id="github.create_pr",
        version="1.0.0",
        description="Create a GitHub Pull Request",
        capabilities=[SkillCapability(name="github.write", scope="repo:nexifyai-dev/*")],
        risk_level=SkillRisk.MEDIUM,
        blast_radius=2,
        requires_approval=True,
        inputs=[
            SkillInput("title", "string", True),
            SkillInput("head", "string", True, "Source branch"),
            SkillInput("base", "string", True, "Target branch"),
            SkillInput("body", "string", False),
        ],
        outputs=[SkillOutput("pr_number", "integer")],
        compensation=SkillCompensation("github.close_pr", "Close the PR", False, True),
        connector="github",
        tags=["github", "write", "pr"],
    ),
    "vercel.deploy": SkillManifest(
        skill_id="vercel.deploy",
        version="1.0.0",
        description="Deploy to Vercel",
        capabilities=[SkillCapability(name="vercel.write", scope="project:frontend")],
        risk_level=SkillRisk.HIGH,
        blast_radius=3,
        requires_approval=True,
        inputs=[
            SkillInput("project", "string", True),
            SkillInput("production", "boolean", False, "Production deployment"),
        ],
        outputs=[SkillOutput("deployment_id", "string")],
        compensation=SkillCompensation("vercel.rollback", "Rollback deployment", True, False),
        connector="vercel",
        tags=["vercel", "write", "deploy"],
    ),
    "supabase.migrate": SkillManifest(
        skill_id="supabase.migrate",
        version="1.0.0",
        description="Execute a governed Supabase migration",
        capabilities=[SkillCapability(name="supabase.write", scope="database:*")],
        risk_level=SkillRisk.CRITICAL,
        blast_radius=3,
        requires_approval=True,
        inputs=[
            SkillInput("sql", "string", True, "Migration SQL"),
            SkillInput("checksum", "string", True, "SHA256 checksum"),
        ],
        outputs=[SkillOutput("migration_id", "string")],
        compensation=SkillCompensation("supabase.rollback_migration", "Rollback migration", False, True),
        connector="supabase",
        tags=["supabase", "write", "migration", "critical"],
    ),
}
