"""
Auto-generate OpenAPI spec, Swagger UI config, and documentation.
"""
import json
from typing import Any


def generate_openapi_spec(
    project_name: str,
    endpoints: list[dict],
    version: str = "1.0.0",
) -> dict:
    """
    Generate a complete OpenAPI 3.0 specification from endpoint definitions.
    """
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": f"{project_name} API",
            "description": f"Auto-generated REST API documentation for {project_name}",
            "version": version,
            "contact": {"name": "API Gen Platform"},
        },
        "servers": [
            {"url": "http://localhost:8000", "description": "Local development"},
        ],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                },
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                },
            },
        },
        "tags": [],
    }

    # Collect unique tags
    seen_tags = set()

    for ep in endpoints:
        method = ep["method"].lower()
        path = ep["path"]

        # Tags
        for tag in ep.get("tags", []):
            if tag not in seen_tags:
                seen_tags.add(tag)
                spec["tags"].append({"name": tag})

        # Build operation
        operation = {
            "summary": ep.get("summary", ""),
            "tags": ep.get("tags", []),
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": ep.get("response_schema", {"type": "object"}),
                        },
                    },
                },
                "422": {"description": "Validation error"},
                "500": {"description": "Internal server error"},
            },
        }

        # Request body
        if ep.get("request_body"):
            model_name = _to_pascal_case(ep["function_name"]) + "Request"
            spec["components"]["schemas"][model_name] = ep["request_body"]
            operation["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{model_name}"},
                        "example": _generate_example(ep["request_body"]),
                    },
                },
            }

        # Query parameters for GET
        if method == "get" and ep.get("parameters"):
            operation["parameters"] = []
            for p in ep["parameters"]:
                operation["parameters"].append({
                    "name": p["name"],
                    "in": "query",
                    "required": p.get("default") is None,
                    "schema": {"type": _python_type_to_openapi(p.get("type", "Any"))},
                })

        # Add to paths
        if path not in spec["paths"]:
            spec["paths"][path] = {}
        spec["paths"][path][method] = operation

    return spec


def generate_example_requests(endpoints: list[dict]) -> dict[str, dict]:
    """Generate example request/response pairs for each endpoint."""
    examples = {}
    for ep in endpoints:
        key = f"{ep['method']} {ep['path']}"
        example = {"method": ep["method"], "path": ep["path"]}

        if ep.get("request_body"):
            example["request_body"] = _generate_example(ep["request_body"])

        example["example_response"] = {
            "success": True,
            "data": _generate_example_value(ep.get("return_type", "Any")),
            "message": "OK",
        }

        if ep["method"] == "GET" and ep.get("parameters"):
            example["query_params"] = {
                p["name"]: _generate_example_value(p.get("type", "Any"))
                for p in ep["parameters"]
            }

        examples[key] = example

    return examples


def _generate_example(schema: dict) -> dict:
    """Generate example data from a JSON Schema."""
    if not schema or schema.get("type") != "object":
        return {}

    example = {}
    for name, prop in schema.get("properties", {}).items():
        ptype = prop.get("type", "string")
        example[name] = _example_for_type(ptype, name)
    return example


def _example_for_type(json_type: str, field_name: str = "") -> Any:
    """Generate example value for a JSON type."""
    examples_by_name = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 25,
        "price": 29.99,
        "image": "base64_encoded_image_data",
        "url": "https://example.com",
        "text": "Sample text input",
        "query": "example search query",
        "description": "A sample description",
        "title": "Sample Title",
        "id": 1,
        "count": 10,
    }

    # Check for field name matches
    for key, val in examples_by_name.items():
        if key in field_name.lower():
            return val

    # Fallback by type
    defaults = {
        "string": "example_string",
        "integer": 42,
        "number": 3.14,
        "boolean": True,
        "array": ["item1", "item2"],
        "object": {"key": "value"},
    }
    return defaults.get(json_type, "example")


def _generate_example_value(py_type: str) -> Any:
    """Generate example value from Python type."""
    mapping = {
        "str": "example result",
        "int": 42,
        "float": 3.14,
        "bool": True,
        "list": ["item1", "item2"],
        "dict": {"key": "value"},
    }
    for key, val in mapping.items():
        if key in py_type.lower():
            return val
    return {"result": "example"}


def _to_pascal_case(name: str) -> str:
    import re
    parts = re.split(r'[_.]', name)
    return "".join(p.capitalize() for p in parts)


def _python_type_to_openapi(py_type: str) -> str:
    mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "dict": "object",
    }
    for key, val in mapping.items():
        if key in py_type.lower():
            return val
    return "string"
