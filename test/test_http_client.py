from dynatrace.http_client import HttpClient


def test_sanitize_params_removes_none_values():
    params = {
        "entitySelector": 'type("HOST")',
        "from": "now-3d",
        "to": None,
        "sort": None,
        "pageSize": 2,
    }

    sanitized = HttpClient._sanitize_params(params)

    assert sanitized == {
        "entitySelector": 'type("HOST")',
        "from": "now-3d",
        "pageSize": 2,
    }
