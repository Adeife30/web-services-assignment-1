from __future__ import annotations

import requests
from fastapi import HTTPException


def fetch_usd_to_eur_rate(exchange_rate_url: str) -> tuple[float, str]:
    try:
        response = requests.get(exchange_rate_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach exchange rate service: {exc}") from exc

    eur_rate = data.get("rates", {}).get("EUR")
    provider = data.get("provider", exchange_rate_url)

    if eur_rate is None:
        raise HTTPException(status_code=502, detail="Exchange rate service did not return an EUR rate")

    return float(eur_rate), str(provider)
