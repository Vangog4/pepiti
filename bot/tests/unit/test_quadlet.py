"""Deployment contract for the always-on service (P1.11). Files only; nothing is installed."""

import configparser
import pathlib

import pytest

Q = pathlib.Path(__file__).resolve().parents[3] / "deploy" / "quadlet"
CONTAINERS = ["pepito-db", "pepito-redis", "pepito-bot", "pepito-api"]


def _active(name):
    """File text without comment lines."""
    lines = (Q / name).read_text().splitlines()
    return "\n".join(line for line in lines if not line.lstrip().startswith("#"))


def _read(name):
    cp = configparser.ConfigParser(strict=False, interpolation=None)
    cp.optionxform = str
    cp.read(Q / name)
    return cp


@pytest.mark.parametrize("name", CONTAINERS)
def test_container_units_are_resilient(name):
    cp = _read(f"{name}.container")
    assert cp["Service"]["Restart"] == "always"
    assert cp["Install"]["WantedBy"] == "multi-user.target"
    c = cp["Container"]
    assert c["HealthCmd"] and c["HealthOnFailure"] == "kill"
    assert "EnvironmentFile" in c
    assert "Network=pepito.network" in _active(f"{name}.container")


@pytest.mark.parametrize("name", ["pepito-db", "pepito-redis"])
def test_datastores_are_never_published(name):
    text = _active(f"{name}.container")
    assert "PublishPort" not in text
    assert "0.0.0.0" not in text


def test_redis_requires_a_password():
    assert "--requirepass" in (Q / "pepito-redis.container").read_text()


def test_app_waits_for_datastores():
    for name in ("pepito-bot", "pepito-api"):
        unit = _read(f"{name}.container")["Unit"]
        assert (
            "pepito-db.service" in unit["Requires"] and "pepito-redis.service" in unit["Requires"]
        )


def test_bot_health_uses_scheduler_heartbeat():
    assert "app.scheduler.jobs.heartbeat" in (Q / "pepito-bot.container").read_text()


def test_compose_does_not_publish_datastores_either():
    compose = (Q.parents[1] / "bot" / "podman-compose.yml").read_text()
    for port in ("5432:5432", "6379:6379", '"5432"', '"6379"'):
        assert port not in compose


def test_backup_rotates_only_its_own_dumps():
    svc = (Q / "pepito-backup.service").read_text()
    assert "-name 'pepito-*.sql.gz'" in svc and "-mtime +7 -delete" in svc
    assert "pg_dump" in svc
    assert _read("pepito-backup.timer")["Timer"]["Persistent"] == "true"


def test_podman_quadlet_generator_accepts_every_unit():
    """Run Podman's own generator (dry run, installs nothing). Catches keys this Podman
    version does not support, which silently drop a unit."""
    import os
    import shutil
    import subprocess

    gen = "/usr/libexec/podman/quadlet"
    if not shutil.which(gen) and not os.path.exists(gen):
        pytest.skip("podman quadlet generator not installed")
    out = subprocess.run(
        [gen, "--dryrun"],
        env={**os.environ, "QUADLET_UNIT_DIRS": str(Q)},
        capture_output=True,
        text=True,
        timeout=30,
    )
    text = out.stdout + out.stderr
    assert "unsupported key" not in text and "converting" not in text, text
    for svc in ("pepito-db", "pepito-redis", "pepito-bot", "pepito-api"):
        assert f"---{svc}.service---" in out.stdout, svc


def test_redis_password_is_escaped_for_systemd():
    """systemd expands $VAR in ExecStart from the *unit* env (empty here); $$ keeps it for sh."""
    text = _active("pepito-redis.container")
    assert "$$REDIS_PASSWORD" in text
    assert "$REDIS_PASSWORD" not in text.replace("$$REDIS_PASSWORD", "")


def test_no_ignored_notify_healthy():
    """Podman 4.9 ignores Notify=healthy; do not claim health-gated startup we do not have."""
    for name in CONTAINERS:
        assert "Notify=healthy" not in _active(f"{name}.container")
