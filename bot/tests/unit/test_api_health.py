"""Health route is registered and public."""


def test_health_route_registered():
    from app.api.routes import routes

    paths = [getattr(r, "path", None) for r in routes]
    assert "/api/health" in paths
