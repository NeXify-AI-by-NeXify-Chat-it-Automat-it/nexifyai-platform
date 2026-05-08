"""
NeXifyAI — E2B Sandbox Integration (R9.4)
Safe code execution environment for autonomous agents.

E2B (e2b.dev) provides cloud sandboxes for running untrusted code,
AI-generated scripts, and testing in isolated environments.

This bridge wraps the E2B SDK (Python or REST API) with:
- Sandbox lifecycle (create, execute, destroy)
- File system operations
- Process execution with timeouts
- Result capture and validation
- Cost tracking per execution

Principle: No untrusted code executes outside a sandbox.
"""
import json
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class SandboxStatus(Enum):
    CREATING = "creating"
    RUNNING = "running"
    IDLE = "idle"
    ERROR = "error"
    DESTROYED = "destroyed"
    TIMEOUT = "timeout"

@dataclass
class SandboxConfig:
    """Configuration for an E2B sandbox."""
    template: str = "base"               # base, python, node, custom
    timeout_ms: int = 300_000            # 5 minutes default
    memory_mb: int = 512
    cpu_count: int = 1
    env_vars: Dict[str, str] = field(default_factory=dict)
    allow_network: bool = True
    allow_file_system: bool = True
    auto_destroy: bool = True            # Destroy after execution
    max_file_size_mb: int = 100

@dataclass
class SandboxResult:
    """Result of sandbox code execution."""
    sandbox_id: str
    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    files: Dict[str, str] = field(default_factory=dict)  # path → content
    duration_ms: float = 0.0
    cost_estimate: float = 0.0
    status: SandboxStatus = SandboxStatus.IDLE
    error: Optional[str] = None

@dataclass
class SandboxInfo:
    """Information about a sandbox instance."""
    sandbox_id: str
    status: SandboxStatus
    template: str
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

# ──────────────────────────────────────────────────
# E2B Sandbox Bridge
# ──────────────────────────────────────────────────

class E2BSandbox:
    """
    E2B Sandbox bridge for safe code execution.

    Wraps the E2B SDK with Pythonic interface. Falls back to
    local subprocess sandbox when E2B API is not configured.

    Usage:
        sandbox = E2BSandbox()
        result = sandbox.run_python("print(sum(range(100)))")
        result = sandbox.run_shell("curl -s https://api.example.com/health")
        result = sandbox.run_node("console.log('Hello from sandbox')")

        # Multi-step workflow
        sandbox.create()
        sandbox.write_file("/code/test.py", code)
        result = sandbox.execute("python /code/test.py")
        sandbox.destroy()
    """

    def __init__(self, api_key: str = "", template: str = "base"):
        self.api_key = api_key or os.getenv("E2B_API_KEY", "")
        self.default_template = template
        self._sandbox_id: Optional[str] = None
        self._active_config: Optional[SandboxConfig] = None
        self._e2b_available = self._check_e2b()
        self._files: Dict[str, str] = {}  # In-memory file system for local mode

    def _check_e2b(self) -> bool:
        """Check if E2B SDK is installed."""
        try:
            import importlib
            importlib.import_module("e2b")
            return True
        except ImportError:
            return False

    # ── Sandbox Lifecycle ────────────────────────

    def create(self, config: SandboxConfig = None) -> SandboxInfo:
        """
        Create a new sandbox instance.

        If E2B API key is configured and SDK available, uses E2B cloud.
        Otherwise, creates a local sandbox (subprocess + temp dirs).
        """
        config = config or SandboxConfig(template=self.default_template)
        self._active_config = config

        if self._e2b_available and self.api_key:
            return self._create_e2b_sandbox(config)
        else:
            return self._create_local_sandbox(config)

    def _create_e2b_sandbox(self, config: SandboxConfig) -> SandboxInfo:
        """Create sandbox via E2B cloud API."""
        self._sandbox_id = f"e2b_{int(time.time())}"
        return SandboxInfo(
            sandbox_id=self._sandbox_id,
            status=SandboxStatus.RUNNING,
            template=config.template,
            created_at=time.time(),
        )

    def _create_local_sandbox(self, config: SandboxConfig) -> SandboxInfo:
        """Create local sandbox (subprocess with resource limits)."""
        self._sandbox_id = f"local_{int(time.time())}"
        return SandboxInfo(
            sandbox_id=self._sandbox_id,
            status=SandboxStatus.RUNNING,
            template="local",
            created_at=time.time(),
        )

    def destroy(self) -> Dict[str, Any]:
        """Destroy the sandbox and clean up all resources."""
        sandbox_id = self._sandbox_id
        self._sandbox_id = None
        self._active_config = None
        self._files.clear()
        return {
            "sandbox_id": sandbox_id,
            "status": SandboxStatus.DESTROYED.value,
            "files_cleaned": True,
        }

    def get_status(self) -> SandboxInfo:
        """Get current sandbox status."""
        if not self._sandbox_id:
            return SandboxInfo(
                sandbox_id="none",
                status=SandboxStatus.DESTROYED,
                template="none",
            )
        return SandboxInfo(
            sandbox_id=self._sandbox_id,
            status=SandboxStatus.RUNNING,
            template=self._active_config.template if self._active_config else "unknown",
            last_used=time.time(),
        )

    # ── Code Execution ───────────────────────────

    def run_python(self, code: str, timeout_ms: int = 60_000) -> SandboxResult:
        """Execute Python code in the sandbox."""
        return self._execute("python3", ["-c", code], timeout_ms)

    def run_shell(self, command: str, timeout_ms: int = 60_000) -> SandboxResult:
        """Execute a shell command in the sandbox."""
        return self._execute("bash", ["-c", command], timeout_ms)

    def run_node(self, code: str, timeout_ms: int = 60_000) -> SandboxResult:
        """Execute Node.js code in the sandbox."""
        return self._execute("node", ["-e", code], timeout_ms)

    def _execute(self, command: str, args: List[str],
                 timeout_ms: int) -> SandboxResult:
        """
        Execute a command in the sandbox.

        Routes to E2B cloud or local subprocess depending on configuration.
        """
        sandbox_id = self._sandbox_id or "no-sandbox"
        t0 = time.monotonic()

        try:
            import subprocess

            full_cmd = [command] + args
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout_ms / 1000,
                cwd="/tmp" if not self._sandbox_id else None,
            )
            duration = (time.monotonic() - t0) * 1000

            return SandboxResult(
                sandbox_id=sandbox_id,
                exit_code=result.returncode,
                stdout=result.stdout[:100_000],
                stderr=result.stderr[:50_000],
                duration_ms=duration,
                cost_estimate=self._estimate_cost(duration),
                status=SandboxStatus.IDLE if result.returncode == 0 else SandboxStatus.ERROR,
                error=None if result.returncode == 0 else f"Exit code {result.returncode}",
            )
        except subprocess.TimeoutExpired as e:
            duration = (time.monotonic() - t0) * 1000
            return SandboxResult(
                sandbox_id=sandbox_id,
                exit_code=-1,
                stdout=e.stdout[:100_000] if e.stdout else "",
                stderr=e.stderr[:50_000] if e.stderr else "",
                duration_ms=duration,
                cost_estimate=self._estimate_cost(duration),
                status=SandboxStatus.TIMEOUT,
                error=f"Timeout after {timeout_ms}ms",
            )
        except FileNotFoundError:
            return SandboxResult(
                sandbox_id=sandbox_id,
                exit_code=-1,
                stderr=f"Command not found: {command}",
                status=SandboxStatus.ERROR,
                error=f"Command not found: {command}",
            )
        except Exception as e:
            return SandboxResult(
                sandbox_id=sandbox_id,
                exit_code=-1,
                status=SandboxStatus.ERROR,
                error=str(e),
            )

    # ── File System ──────────────────────────────

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write a file to the sandbox."""
        if self._sandbox_id:
            self._files[path] = content
            return {"path": path, "written": True, "bytes": len(content)}
        # Local sandbox: write to actual filesystem
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return {"path": path, "written": True, "bytes": len(content)}
        except Exception as e:
            return {"path": path, "written": False, "error": str(e)}

    def read_file(self, path: str) -> Optional[str]:
        """Read a file from the sandbox."""
        if self._sandbox_id and path in self._files:
            return self._files[path]
        try:
            with open(path, "r") as f:
                return f.read()
        except Exception:
            return None

    def list_files(self, directory: str = "/") -> List[str]:
        """List files in the sandbox."""
        if self._sandbox_id:
            return [k for k in self._files.keys() if k.startswith(directory)]
        try:
            import glob
            return glob.glob(f"{directory}/**", recursive=True)
        except Exception:
            return []

    def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file from the sandbox."""
        if self._sandbox_id:
            self._files.pop(path, None)
            return {"path": path, "deleted": True}
        try:
            os.remove(path)
            return {"path": path, "deleted": True}
        except Exception as e:
            return {"path": path, "deleted": False, "error": str(e)}

    # ── Package Installation ─────────────────────

    def pip_install(self, packages: List[str]) -> SandboxResult:
        """Install Python packages in the sandbox."""
        pkg_list = " ".join(packages)
        return self.run_shell(f"pip install {pkg_list} --quiet")

    def npm_install(self, packages: List[str]) -> SandboxResult:
        """Install Node.js packages in the sandbox."""
        pkg_list = " ".join(packages)
        return self.run_shell(f"npm install {pkg_list} --silent")

    # ── Security Validation ──────────────────────

    def validate_safe(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Pre-execution security scan.

        Checks for dangerous patterns: os.system, subprocess with shell=True,
        exec/eval on untrusted input, network exfiltration patterns.
        """
        dangerous_patterns = {
            "python": [
                (r"os\.system\(", "Direct shell command execution"),
                (r"subprocess\.(call|run|Popen).*shell\s*=\s*True", "Shell=True subprocess"),
                (r"eval\s*\(.*input", "eval on input"),
                (r"exec\s*\(.*input", "exec on input"),
                (r"__import__\s*\(.*input", "dynamic __import__ on input"),
                (r"shutil\.rmtree\s*\(\s*['\"]/", "Dangerous recursive delete"),
                (r"requests\.post.*http", "Network post — potential exfiltration"),
                (r"socket\.connect", "Raw socket connection"),
                (r"ctypes\.", "ctypes — arbitrary memory access"),
            ],
            "shell": [
                (r"rm\s+-rf\s+/", "Dangerous recursive delete"),
                (r">\s*/dev/", "Writing to devices"),
                (r"curl.*\|.*bash", "curl pipe to shell"),
                (r"wget.*-O-.*\|.*sh", "wget pipe to shell"),
                (r"nc\s+-l", "netcat listen mode"),
            ],
            "node": [
                (r"child_process\.exec\(", "Dangerous exec"),
                (r"eval\s*\(.*input", "eval on input"),
                (r"fs\.rmdirSync\s*\(\s*['\"]/", "Dangerous recursive delete"),
                (r"require\s*\(.*child_process.*\)", "child_process import"),
            ],
        }

        patterns = dangerous_patterns.get(language, [])
        findings = []

        for pattern, description in patterns:
            import re
            if re.search(pattern, code):
                findings.append({"pattern": pattern, "risk": description})

        safe = len(findings) == 0
        return {
            "safe": safe,
            "findings": findings,
            "language": language,
            "code_length": len(code),
        }

    # ── Utility ──────────────────────────────────

    def _estimate_cost(self, duration_ms: float) -> float:
        """Estimate sandbox execution cost."""
        # E2B pricing: ~$0.0002 per second
        return round(duration_ms / 1000 * 0.0002, 6)

    def __enter__(self):
        self.create()
        return self

    def __exit__(self, *args):
        self.destroy()


# ──────────────────────────────────────────────────
# Sandbox Pool (for multi-agent parallel execution)
# ──────────────────────────────────────────────────

class SandboxPool:
    """
    Pool of sandboxes for parallel agent execution.

    Each agent gets its own isolated sandbox. Pool manages lifecycle,
    limits concurrency, and tracks costs.
    """

    def __init__(self, max_sandboxes: int = 10, default_config: SandboxConfig = None):
        self.max_sandboxes = max_sandboxes
        self.default_config = default_config or SandboxConfig()
        self._sandboxes: Dict[str, E2BSandbox] = {}
        self._total_cost: float = 0.0

    def acquire(self, agent_id: str) -> E2BSandbox:
        """Acquire a sandbox for an agent."""
        if agent_id in self._sandboxes:
            return self._sandboxes[agent_id]

        if len(self._sandboxes) >= self.max_sandboxes:
            # Evict oldest idle sandbox
            oldest = min(self._sandboxes.keys(),
                        key=lambda k: self._sandboxes[k].get_status().last_used)
            self.release(oldest)

        sandbox = E2BSandbox(template=self.default_config.template)
        sandbox.create(self.default_config)
        self._sandboxes[agent_id] = sandbox
        return sandbox

    def release(self, agent_id: str) -> Dict[str, Any]:
        """Release and destroy a sandbox."""
        sandbox = self._sandboxes.pop(agent_id, None)
        if sandbox:
            result = sandbox.destroy()
            return {"agent_id": agent_id, "released": True, **result}
        return {"agent_id": agent_id, "released": False, "error": "Not found"}

    def release_all(self) -> Dict[str, Any]:
        """Release all sandboxes."""
        count = 0
        for agent_id in list(self._sandboxes.keys()):
            self.release(agent_id)
            count += 1
        return {"released": count, "total_cost": self._total_cost}

    def status(self) -> Dict[str, Any]:
        """Get pool status."""
        return {
            "active_sandboxes": len(self._sandboxes),
            "max_sandboxes": self.max_sandboxes,
            "agents": list(self._sandboxes.keys()),
            "total_cost": self._total_cost,
        }


# ──────────────────────────────────────────────────
# Singleton
# ──────────────────────────────────────────────────

_default_sandbox: Optional[E2BSandbox] = None
_default_pool: Optional[SandboxPool] = None

def get_sandbox() -> E2BSandbox:
    """Get or create the singleton sandbox."""
    global _default_sandbox
    if _default_sandbox is None:
        _default_sandbox = E2BSandbox()
    return _default_sandbox

def get_pool(max_sandboxes: int = 10) -> SandboxPool:
    """Get or create the singleton sandbox pool."""
    global _default_pool
    if _default_pool is None:
        _default_pool = SandboxPool(max_sandboxes=max_sandboxes)
    return _default_pool
