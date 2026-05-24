"""
LangChain Tool Registry — Enterprise Tool-Katalog
==================================================
Ersetzt: mcp_tool_registry.py (51 Zeilen), Custom-Tools in agent_executor.py (537 Zeilen)

Alle Tools sind @tool-decorierte Funktionen mit:
- Typisierte Parameter (Pydantic-kompatibel)
- Docstrings (werden vom LLM als Tool-Beschreibung verwendet)
- Error-Handling (jedes Tool fängt eigene Fehler)
"""
import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Optional

from langchain_core.tools import tool
from langchain_community.tools import ShellTool

logger = logging.getLogger("nexifyai.tools")

# ─── Shell / System ───────────────────────────────────────────────────────────

@tool
def run_shell(command: str, timeout: int = 30) -> str:
    """Führe einen Shell-Befehl aus. Nützlich für: File-Operationen, Git, Deployment, System-Abfragen.
    
    Args:
        command: Der auszuführende Shell-Befehl
        timeout: Timeout in Sekunden (Default: 30)
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
        error = result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr
        if result.returncode != 0:
            return f"Exit code {result.returncode}\nStderr: {error}\nStdout: {output}"
        return output or "(leere Ausgabe)"
    except subprocess.TimeoutExpired:
        return f"Fehler: Befehl nach {timeout}s abgebrochen"
    except Exception as e:
        return f"Fehler: {str(e)}"


# ─── GitHub / Entwicklung ─────────────────────────────────────────────────────

@tool
def create_github_issue(title: str, body: str, labels: Optional[list] = None) -> str:
    """Erstelle ein GitHub Issue im aktuellen Repository.
    
    Args:
        title: Titel des Issues
        body: Beschreibung des Issues (Markdown)
        labels: Optional Liste von Labels (z.B. ["bug", "security"])
    """
    try:
        labels_str = ",".join(labels) if labels else ""
        cmd = f'gh issue create --title "{title}" --body "{body}"'
        if labels_str:
            cmd += f' --label "{labels_str}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return f"Issue erstellt: {result.stdout.strip()}"
        return f"Fehler: {result.stderr}"
    except Exception as e:
        return f"Fehler: {str(e)}"


@tool
def search_code(query: str, path: str = ".") -> str:
    """Durchsuche Codebase mit regulärem Ausdruck. Nützlich für: Code-Reviews, Bug-Jagd, Refactoring.
    
    Args:
        query: Suchbegriff oder Regex
        path: Pfad zum Durchsuchen (Default: aktuelles Verzeichnis)
    """
    try:
        result = subprocess.run(
            f'rg -n --context 2 "{query}" {path}',
            shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        if not output:
            return f"Keine Ergebnisse für '{query}'"
        if len(output) > 3000:
            output = output[:3000] + "\n...(gekürzt)"
        return output
    except Exception as e:
        return f"Fehler: {str(e)}"


# ─── Knowledge / Brain ────────────────────────────────────────────────────────

@tool
def brain_search(query: str, limit: int = 5) -> str:
    """Durchsuche das Enterprise Brain (Wissensdatenbank). 
    Enthält: Architektur-Entscheidungen, Playbooks, Incident-Reports, Policies.
    
    Args:
        query: Suchbegriff
        limit: Maximale Anzahl Ergebnisse (Default: 5)
    """
    try:
        import httpx
        brain_url = os.getenv("BRAIN_API_URL", "http://localhost:8420")
        response = httpx.get(
            f"{brain_url}/query",
            params={"query": query, "limit": limit},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", data.get("points", []))
            if not results:
                return f"Keine Brain-Ergebnisse für '{query}'"
            formatted = []
            for r in results[:limit]:
                payload = r.get("payload", r)
                formatted.append(
                    f"[{payload.get('category', '?')}] {payload.get('content', str(payload))[:300]}"
                )
            return "\n---\n".join(formatted)
        return f"Brain API Fehler: HTTP {response.status_code}"
    except Exception as e:
        return f"Brain nicht erreichbar: {str(e)}"


@tool
def store_brain_note(content: str, category: str = "note", tags: Optional[list] = None) -> str:
    """Speichere eine Notiz im Enterprise Brain (Wissensdatenbank).
    
    Args:
        content: Der Inhalt der Notiz
        category: Kategorie (note, decision, incident, learning, policy)
        tags: Optional Liste von Tags
    """
    try:
        import httpx
        brain_url = os.getenv("BRAIN_API_URL", "http://localhost:8420")
        payload = {
            "content": content,
            "category": category,
            "tags": tags or [],
            "timestamp": datetime.utcnow().isoformat(),
        }
        response = httpx.post(f"{brain_url}/store", json=payload, timeout=10)
        if response.status_code in (200, 201):
            return f"Notiz gespeichert (Kategorie: {category})"
        return f"Fehler: HTTP {response.status_code}"
    except Exception as e:
        return f"Brain nicht erreichbar: {str(e)}"


# ─── Supabase / Datenbank ─────────────────────────────────────────────────────

@tool
def query_database(sql: str) -> str:
    """Führe eine SQL-Abfrage auf der Supabase-Datenbank aus (READ-ONLY).
    Nur SELECT-Abfragen erlaubt.
    
    Args:
        sql: SELECT-SQL-Abfrage
    """
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return "Fehler: Nur SELECT-Abfragen erlaubt (Read-Only)"
    try:
        import asyncpg
        import asyncio
        
        dsn = os.getenv("ALT_SUPABASE_POSTGRESQL")
        if not dsn:
            return "Fehler: Keine Datenbank-URL konfiguriert"
        
        async def run():
            conn = await asyncpg.connect(dsn)
            try:
                rows = await conn.fetch(sql)
                await conn.close()
                if not rows:
                    return "Keine Ergebnisse"
                # Formatiere als JSON-Array
                result = [dict(r) for r in rows]
                return json.dumps(result, default=str, indent=2)[:3000]
            except Exception as e:
                await conn.close()
                return f"Datenbankfehler: {str(e)}"
        
        return asyncio.run(run())
    except Exception as e:
        return f"Fehler: {str(e)}"


# ─── System Health ────────────────────────────────────────────────────────────

@tool
def check_system_health(endpoint: str = None) -> str:
    """Überprüfe den Health-Status eines Services.
    
    Args:
        endpoint: Health-Endpoint URL (Default: Backend-Health)
    """
    try:
        import httpx
        url = endpoint or f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/health"
        response = httpx.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=2)
        return f"Health-Check fehlgeschlagen: HTTP {response.status_code}"
    except Exception as e:
        return f"Health-Check fehlgeschlagen: {str(e)}"


# ─── Tool Registry ────────────────────────────────────────────────────────────

def get_all_tools():
    """Alle verfügbaren Tools als Liste."""
    return [
        run_shell,
        create_github_issue,
        search_code,
        brain_search,
        store_brain_note,
        query_database,
        check_system_health,
    ]


def get_agent_tools(agent_type: str = "default"):
    """Rollenbasierte Tool-Auswahl.
    
    Args:
        agent_type: 'developer', 'research', 'admin', 'oracle', 'default'
    """
    all_tools = get_all_tools()
    
    role_tools = {
        "developer": [run_shell, search_code, create_github_issue, brain_search],
        "research": [brain_search, check_system_health],
        "admin": [run_shell, query_database, brain_search, store_brain_note, check_system_health],
        "oracle": [brain_search, store_brain_note, query_database, check_system_health],
        "default": all_tools,
    }
    
    return role_tools.get(agent_type, all_tools)
