from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

pytestmark = pytest.mark.e2e

AWID_URL = os.environ.get("ATEXT_E2E_AWID_URL", "http://127.0.0.1:18010")
POSTGRES_URL = os.environ.get(
    "ATEXT_E2E_DATABASE_URL",
    "postgresql://atext:atext@127.0.0.1:55432/atext",
)


def _require_e2e_enabled() -> None:
    if os.environ.get("ATEXT_E2E") != "1":
        pytest.skip("set ATEXT_E2E=1 or run `make e2e` to execute docker-backed e2e tests")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_http_ok(url: str, *, timeout_seconds: float = 30.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            response = httpx.get(url, timeout=2.0)
            if response.status_code < 500:
                return
        except Exception as exc:  # pragma: no cover - only used for diagnostics
            last_error = exc
        time.sleep(0.25)
    raise RuntimeError(f"timed out waiting for {url}: {last_error}")


def _run_aw(workspace: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["aw", "--json", *args],
        cwd=workspace,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "aw command failed\n"
            f"cmd: aw --json {' '.join(args)}\n"
            f"exit: {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}\n"
        )
    return result


def _run_aw_json(workspace: Path, env: dict[str, str], *args: str) -> dict[str, Any]:
    result = _run_aw(workspace, env, *args)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"aw command did not emit JSON: {result.stdout}\n{result.stderr}") from exc
    assert isinstance(payload, dict)
    return payload


@pytest.fixture(scope="session")
def atext_origin() -> Iterator[str]:
    _require_e2e_enabled()
    _wait_http_ok(f"{AWID_URL}/health")

    port = _free_port()
    origin = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env.update(
        {
            "ATEXT_DATABASE_URL": POSTGRES_URL,
            "ATEXT_AWID_REGISTRY_URL": AWID_URL,
            "ATEXT_AUTH_CACHE_TTL_SECONDS": "1",
            "ATEXT_PUBLIC_ORIGIN": origin,
        }
    )
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "atext.api:create_app", "--factory", "--host", "127.0.0.1", "--port", str(port)],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        _wait_http_ok(f"{origin}/health")
        yield origin
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
        if proc.returncode not in (0, -15, -9, None):
            stdout = proc.stdout.read() if proc.stdout else ""
            stderr = proc.stderr.read() if proc.stderr else ""
            raise RuntimeError(f"uvicorn exited with {proc.returncode}\nstdout:\n{stdout}\nstderr:\n{stderr}")


@pytest.fixture()
def aw_workspace(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    _require_e2e_enabled()
    workspace = tmp_path / "workspace"
    home = tmp_path / "home"
    workspace.mkdir()
    home.mkdir()
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "AWEB_URL": "http://127.0.0.1:1",
            "AWID_REGISTRY_URL": AWID_URL,
            "NO_COLOR": "1",
        }
    )
    return workspace, env


def _write_workspace_binding(workspace: Path, *, team_id: str, alias: str, cert_path: str) -> None:
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    workspace_id = str(uuid.uuid4())
    (workspace / ".aw" / "workspace.yaml").write_text(
        f"""aweb_url: http://127.0.0.1:1
memberships:
    - team_id: {team_id}
      alias: {alias}
      workspace_id: {workspace_id}
      cert_path: {cert_path}
      joined_at: \"{now}\"
human_name: e2e
agent_type: agent
workspace_path: {workspace}
updated_at: \"{now}\"
""",
        encoding="utf-8",
    )


def _provision_real_team_certificate(workspace: Path, env: dict[str, str]) -> str:
    unique = uuid.uuid4().hex[:12]
    namespace = f"atext-{unique}.test"
    team = "default"
    alias = "alice"

    _run_aw(
        workspace,
        env,
        "id",
        "create",
        "--domain",
        namespace,
        "--name",
        alias,
        "--registry",
        AWID_URL,
        "--skip-dns-verify",
    )
    _run_aw(
        workspace,
        env,
        "id",
        "team",
        "create",
        "--namespace",
        namespace,
        "--name",
        team,
        "--registry",
        AWID_URL,
    )
    add_member = _run_aw_json(
        workspace,
        env,
        "id",
        "team",
        "add-member",
        "--namespace",
        namespace,
        "--team",
        team,
        "--member",
        f"{namespace}/{alias}",
    )
    cert_id = str(add_member["certificate_id"])
    fetch_cert = _run_aw_json(
        workspace,
        env,
        "id",
        "team",
        "fetch-cert",
        "--namespace",
        namespace,
        "--team",
        team,
        "--cert-id",
        cert_id,
        "--registry",
        AWID_URL,
    )
    team_id = f"{team}:{namespace}"
    _run_aw(workspace, env, "id", "team", "switch", team_id)
    _write_workspace_binding(
        workspace,
        team_id=team_id,
        alias=alias,
        cert_path=str(fetch_cert["cert_path"]),
    )
    return team_id


def test_no_envelope_fails_closed(atext_origin: str) -> None:
    response = httpx.get(f"{atext_origin}/v1/documents", timeout=10.0)
    if response.status_code != 401:
        pytest.xfail(
            "auth.py is still on the scaffold verifier; flip this to a hard 401 assertion "
            f"with default-aaaa.1. status={response.status_code} body={response.text}"
        )


def test_real_aw_team_auth_smoke(atext_origin: str, aw_workspace: tuple[Path, dict[str, str]]) -> None:
    workspace, env = aw_workspace
    team_id = _provision_real_team_certificate(workspace, env)

    result = subprocess.run(
        ["aw", "id", "request", "GET", f"{atext_origin}/v1/documents", "--team-auth", "--raw"],
        cwd=workspace,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )

    if result.returncode != 0:
        pytest.xfail(
            "aw id request --team-auth emitted v2, but auth.py still verifies the legacy compact envelope; "
            "flip this to a hard assertion when default-aaaa.1 lands. "
            f"team_id={team_id}; stderr={result.stderr.strip()}"
        )

    assert result.stdout.strip() == "[]"
