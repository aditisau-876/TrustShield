import os
import requests
from dotenv import load_dotenv

load_dotenv()

PHISHTANK_URL = "https://checkurl.phishtank.com/checkurl/"


def check_phishtank(url):

    api_key = os.getenv("PHISHTANK_API_KEY")

    if not api_key:
        return {
            "available": False,
            "listed": False,
            "source": "phishtank",
            "reason": "API key not configured"
        }

    try:

        response = requests.post(
            PHISHTANK_URL,
            data={
                "url": url,
                "format": "json"
            },
            headers={
                "User-Agent": "URL-Threat-Intelligence-System"
            },
            timeout=10
        )

        if response.status_code != 200:

            return {
                "available": False,
                "listed": False,
                "source": "phishtank",
                "reason": f"HTTP {response.status_code}"
            }

        data = response.json()

        results = data.get("results", {})

        return {
            "available": True,
            "listed": bool(
                results.get("in_database", False)
                and results.get("phish_id")
            ),
            "source": "phishtank",
            "verified": results.get(
                "verified",
                False
            ),
            "online": results.get(
                "online",
                False
            ),
            "phish_id": results.get(
                "phish_id"
            )
        }

    except Exception as exc:

        return {
            "available": False,
            "listed": False,
            "source": "phishtank",
            "reason": str(exc)
        }