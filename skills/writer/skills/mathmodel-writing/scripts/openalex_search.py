#!/usr/bin/env python3
"""Search OpenAlex Works and save the full JSON response without exposing secrets."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


OPENALEX_WORKS_URL = "https://api.openalex.org/works"


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="OpenAlex full-text search query")
    parser.add_argument("--output", required=True, type=Path, help="Destination JSON file")
    parser.add_argument("--per-page", type=int, default=20, choices=range(1, 101), metavar="1..100")
    parser.add_argument("--retries", type=int, default=3, choices=range(1, 6), metavar="1..5")
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Validate options without making a request")
    return parser.parse_args()


def build_request(query: str, per_page: int, api_key: str) -> Request:
    """Build an OpenAlex request using a caller-supplied environment credential."""
    params: dict[str, str | int] = {"search": query, "per_page": per_page}
    if api_key:
        params["api_key"] = api_key
    url = f"{OPENALEX_WORKS_URL}?{urlencode(params)}"
    return Request(url, headers={"User-Agent": "mathmodel-skills/1.1 (+OpenAlex research lookup)"})


def fetch_json(request: Request, retries: int, timeout: float) -> dict:
    """Fetch JSON with urllib and an optional requests fallback."""
    last_error = "unknown error"
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return json.loads(response.read().decode(charset))
        except HTTPError as exc:
            last_error = f"HTTP {exc.code}: {exc.reason}"
            if 400 <= exc.code < 500 and exc.code != 429:
                break
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"

        # Some managed environments route TLS differently for urllib. When the
        # optional requests package is already installed, use it as a fallback;
        # it is never a required dependency.
        try:
            import requests  # type: ignore[import-not-found]
        except ImportError:
            requests = None
        if requests is not None:
            try:
                response = requests.get(
                    request.full_url,
                    headers=dict(request.header_items()),
                    timeout=timeout,
                )
                if 400 <= response.status_code < 500 and response.status_code != 429:
                    raise RuntimeError(f"HTTP {response.status_code}")
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise RuntimeError("OpenAlex returned a non-object JSON payload")
                return payload
            except RuntimeError as exc:
                last_error = str(exc)
                if last_error.startswith("HTTP 4") and "HTTP 429" not in last_error:
                    break
            except requests.RequestException as exc:
                # requests exceptions may embed the full URL, including a key.
                status = getattr(getattr(exc, "response", None), "status_code", None)
                last_error = f"requests HTTP {status}" if status else f"requests {type(exc).__name__} (details redacted)"
            except json.JSONDecodeError:
                last_error = "requests JSONDecodeError"
        if attempt < retries:
            time.sleep(2 ** (attempt - 1))
    raise RuntimeError(last_error)


def main() -> int:
    """Run a search and persist the response as UTF-8 JSON."""
    args = parse_args()
    api_key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if args.dry_run:
        print(
            json.dumps(
                {
                    "endpoint": OPENALEX_WORKS_URL,
                    "query": args.query,
                    "per_page": args.per_page,
                    "api_key_configured": bool(api_key),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if not api_key:
        print(
            "ERROR: OPENALEX_API_KEY is required for OpenAlex API requests. "
            "Get a free key at https://openalex.org/settings/api and expose it "
            "through the environment, not a command-line argument.",
            file=sys.stderr,
        )
        return 2
    request = build_request(args.query, args.per_page, api_key)
    try:
        payload = fetch_json(request, args.retries, args.timeout)
    except RuntimeError as exc:
        print(f"ERROR: OpenAlex request failed after {args.retries} attempt(s): {exc}", file=sys.stderr)
        return 1

    # Record non-secret provenance next to the unmodified API payload.
    document = {
        "request": {
            "endpoint": OPENALEX_WORKS_URL,
            "query": args.query,
            "per_page": args.per_page,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "api_key_configured": True,
        },
        "response": payload,
    }
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
