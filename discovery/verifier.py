"""
Live API Verification — health checks, doc link validation, response time measurement.
"""
import asyncio
import time
from datetime import datetime
from typing import Optional

import httpx

from config import HEALTH_CHECK_TIMEOUT, MAX_CONCURRENT_CHECKS


async def check_endpoint(
    url: str,
    timeout: int = HEALTH_CHECK_TIMEOUT,
) -> dict:
    """
    Perform a single HTTP health check.
    Returns: {is_reachable, status_code, response_ms, error}
    """
    if not url or url.startswith("https://YOUR_"):
        return {
            "is_reachable": False,
            "status_code": None,
            "response_ms": None,
            "error": "URL is a placeholder or empty",
        }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            start = time.perf_counter()
            resp = await client.get(url)
            elapsed = int((time.perf_counter() - start) * 1000)
            return {
                "is_reachable": resp.status_code < 500,
                "status_code": resp.status_code,
                "response_ms": elapsed,
                "error": "",
            }
    except httpx.TimeoutException:
        return {"is_reachable": False, "status_code": None, "response_ms": None, "error": "Timeout"}
    except httpx.ConnectError as e:
        return {"is_reachable": False, "status_code": None, "response_ms": None, "error": f"Connection error: {e}"}
    except Exception as e:
        return {"is_reachable": False, "status_code": None, "response_ms": None, "error": str(e)}


async def check_documentation(url: str) -> bool:
    """Verify that the documentation URL is reachable."""
    if not url:
        return False
    result = await check_endpoint(url)
    return result["is_reachable"]


async def verify_api(
    base_url: str,
    documentation_url: str,
    api_name: str = "",
) -> dict:
    """
    Full verification of an API: endpoint health + documentation link.
    """
    endpoint_check, doc_check = await asyncio.gather(
        check_endpoint(base_url),
        check_documentation(documentation_url),
    )

    return {
        "api_name": api_name,
        "is_reachable": endpoint_check["is_reachable"],
        "status_code": endpoint_check["status_code"],
        "response_ms": endpoint_check["response_ms"],
        "doc_reachable": doc_check,
        "error": endpoint_check["error"],
        "checked_at": datetime.utcnow().isoformat(),
    }


async def batch_verify(apis: list[dict], max_concurrent: int = MAX_CONCURRENT_CHECKS) -> list[dict]:
    """
    Verify multiple APIs concurrently with a semaphore to limit parallelism.
    Each dict in apis must have: base_url, documentation_url, name
    """
    sem = asyncio.Semaphore(max_concurrent)

    async def _verify(api: dict) -> dict:
        async with sem:
            return await verify_api(
                base_url=api.get("base_url", ""),
                documentation_url=api.get("documentation_url", ""),
                api_name=api.get("name", ""),
            )

    return await asyncio.gather(*[_verify(a) for a in apis])
