            ["git", "log", "-1", "--format=%H|%s|%ai"],
            capture_output=True, text=True, timeout=10,
            cwd="/opt/nexifyai-platform"
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split("|")
            report["commit"] = parts[0] if len(parts) > 0 else ""
            report["last_deploy"] = parts[2] if len(parts) > 2 else ""
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
            cwd="/opt/nexifyai-platform"
        )
        report["branch"] = result.stdout.strip()
    except Exception:
        pass

    # Check if backend is running
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get("http://127.0.0.1:8001/api/health")
            if resp.status_code == 200:
                report["status"] = "healthy"
    except Exception:
        report["status"] = "backend_down"

    return report


# ─── Supabase Auth JWT Validation Helper ───
async def validate_supabase_jwt(token: str) -> dict | None:
    """Validate a Supabase JWT token and return user info if valid."""
    import jwt as pyjwt
    supabase_jwt_secret = os.environ.get("SUPABASE_JWT_SECRET", "")
    if not supabase_jwt_secret:
        return None

    try:
        payload = pyjwt.decode(token, supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")
        email = payload.get("email") or payload.get("sub")
        role = payload.get("user_metadata", {}).get("role") or payload.get("app_metadata", {}).get("role")
        return {"email": email, "role": role, "id": payload.get("sub")}
    except Exception:
        return None
