import os
import json
import requests
from typing import Dict, Any, Optional


def get_n8n_webhook_url() -> Optional[str]:
    """Retrieve n8n Webhook URL from environment or Streamlit secrets."""
    url = os.getenv("N8N_WEBHOOK_URL")
    if url:
        return url.strip()
    try:
        import streamlit as st
        if "N8N_WEBHOOK_URL" in st.secrets:
            return st.secrets["N8N_WEBHOOK_URL"].strip()
    except Exception:
        pass
    return None


def send_to_n8n_webhook(payload: Dict[str, Any], webhook_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Send the finalized travel itinerary payload to the n8n automation webhook.
    Returns response status and message.
    """
    target_url = webhook_url or get_n8n_webhook_url()

    if not target_url or "your-n8n-instance" in target_url:
        return {
            "success": False,
            "status_code": 0,
            "message": "n8n Webhook URL is not configured. Please set N8N_WEBHOOK_URL in .env or Streamlit secrets."
        }

    try:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AgenticTravelItineraryGenerator/1.0"
        }
        response = requests.post(target_url, json=payload, headers=headers, timeout=12)

        if response.status_code in [200, 201, 202]:
            return {
                "success": True,
                "status_code": response.status_code,
                "message": f"Successfully triggered n8n workflow! Status: {response.status_code}",
                "data": response.text[:200]
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "message": f"n8n webhook returned HTTP {response.status_code}: {response.text[:200]}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "status_code": 0,
            "message": f"Failed to connect to n8n webhook: {str(e)}"
        }
