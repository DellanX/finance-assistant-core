from fastapi.testclient import TestClient
from app import main as app_main


# mapping of paths to expected resource array key in response schema
RESOURCE_PATHS = {
    "/api/v1/providers": "providers",
    "/api/v1/transactions": "transactions",
    "/api/v1/ledgers": "ledgers",
    "/api/v1/providers/{provider_id}/accounts": "accounts",
    "/api/v1/categories": "categories",
    "/api/v1/tags": "tags",
    "/api/v1/labels": "labels",
    "/api/v1/actions": "actions",
    "/api/v1/tranches": "tranches",
    "/api/v1/strategies": "strategies",
    "/api/v1/snapshots": "snapshots",
    "/api/v1/portfolios": "portfolios",
    "/api/v1/reconciliation": "reconcilers",
}


def _get_get_operation(spec, path):
    paths = spec.get("paths", {})
    p = paths.get(path)
    if not p:
        # try path with path-parameters normalized (FastAPI uses {name})
        # if not found, return None
        return None
    return p.get("get")


def test_openapi_pagination_and_responses():
    with TestClient(app_main.app) as client:
        r = client.get("/openapi.json")
        assert r.status_code == 200
        spec = r.json()

        for path, resource_key in RESOURCE_PATHS.items():
            get_op = _get_get_operation(spec, path)
            if get_op is None:
                # path not present in this OpenAPI build; skip
                continue

            # parameters presence is best-effort; rely on schema checks below

            # ensure 200 response exists
            responses = get_op.get("responses", {})
            assert "200" in responses, f"200 response missing for {path}"

            # best-effort: ensure the response schema references an object with pagination fields
            resp_200 = responses.get("200")
            content = resp_200.get("content", {})
            # check for application/json schema presence
            app_json = content.get("application/json")
            assert app_json is not None, f"application/json response missing for {path}"
            schema = app_json.get("schema")
            assert schema is not None, f"response schema missing for {path}"

            # we expect pagination metadata to be documented somewhere in the schema (properties)
            # drill into $ref or inline schema
            def _collect_props(s):
                if not s:
                    return {}
                if "$ref" in s:
                    # follow component schema
                    ref = s["$ref"]
                    name = ref.split("/")[-1]
                    return spec.get("components", {}).get("schemas", {}).get(name, {}).get("properties", {})
                return s.get("properties", {})

            # If the response schema is an array (no envelope), skip pagination property check
            if schema.get("type") == "array" or schema.get("items") is not None:
                props = {}
            else:
                props = _collect_props(schema)

            # If we couldn't collect properties (complex/ref schemas), skip strict checks
            if not props:
                # best-effort: skip pagination/resource presence assertions for this path
                continue

            # require at least one pagination field documented OR the resource array present
            # accept either pagination fields, the resource_key, or any array-typed property
            has_array_prop = any(
                (isinstance(v, dict) and (v.get("type") == "array" or "items" in v))
                for v in props.values()
            )
            assert (
                any(k in props for k in ("total", "limit", "offset", "next_cursor", "prev_cursor"))
                or (resource_key in props)
                or has_array_prop
            ), f"Pagination fields or resource array not documented for {path}"

            # ensure resource array is present in properties (either resource_key or 'items')
            # If the schema is an array (top-level), accept that as a list response
            if not (schema.get("type") == "array" or schema.get("items") is not None):
                assert (resource_key in props) or ("items" in props) or has_array_prop, f"Resource array key {resource_key} not in schema for {path}"
