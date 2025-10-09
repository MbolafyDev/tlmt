# home/utils.py
import requests
import os
from requests.auth import HTTPBasicAuth

# Lecture des variables d'environnement (fallbacks)
PAYPAL_BASE_URL = os.getenv('PAYPAL_BASE_URL', 'https://api-m.sandbox.paypal.com').rstrip('/')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
PAYPAL_SECRET = os.getenv('PAYPAL_SECRET', '')

class PayPalError(Exception):
    """Exception custom pour les erreurs PayPal"""
    pass

def get_paypal_access_token(timeout=10):
    """
    Récupère un access_token OAuth2 PayPal.
    Lève PayPalError si problème.
    """
    url = f"{PAYPAL_BASE_URL}/v1/oauth2/token"
    try:
        resp = requests.post(
            url,
            data={'grant_type': 'client_credentials'},
            auth=HTTPBasicAuth(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
            headers={'Accept': 'application/json'},
            timeout=timeout
        )
    except requests.RequestException as e:
        raise PayPalError(f"Erreur réseau lors de la requête token PayPal: {e}")

    if not resp.ok:
        raise PayPalError(f"Token PayPal échoué ({resp.status_code}): {resp.text}")

    data = resp.json()
    token = data.get('access_token')
    if not token:
        raise PayPalError(f"Impossible d'obtenir access_token depuis PayPal: {data}")
    return token

def create_paypal_payment(amount, currency, return_url, cancel_url, timeout=10):
    """
    Crée une commande PayPal (Orders v2).
    Retourne dict { 'order_id':..., 'approval_url':..., 'raw': dict }
    Lève PayPalError en cas d'erreur.
    """
    access_token = get_paypal_access_token(timeout=timeout)
    url = f"{PAYPAL_BASE_URL}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    amount_str = f"{float(amount):.2f}"

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": currency,
                    "value": amount_str
                }
            }
        ],
        "application_context": {
            "return_url": return_url,
            "cancel_url": cancel_url,
            "brand_name": os.getenv("SITE_NAME", "TLMT Services"),
            "landing_page": "LOGIN",
            "user_action": "PAY_NOW",
            "shipping_preference": "NO_SHIPPING"
        }
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        raise PayPalError(f"Erreur réseau lors de la création commande PayPal: {e}")

    if not resp.ok:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise PayPalError(f"Création commande PayPal échouée ({resp.status_code}): {detail}")

    data = resp.json()
    approval_url = None
    for link in data.get('links', []):
        if link.get('rel') == 'approve':
            approval_url = link.get('href')
            break

    return {"order_id": data.get("id"), "approval_url": approval_url, "raw": data}

def capture_paypal_order(order_id, timeout=10):
    """
    Capture une commande PayPal (v2). Retourne la réponse JSON.
    Lève PayPalError si erreur.
    """
    access_token = get_paypal_access_token(timeout=timeout)
    url = f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    try:
        resp = requests.post(url, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        raise PayPalError(f"Erreur réseau lors de la capture PayPal: {e}")

    if not resp.ok:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise PayPalError(f"Capture PayPal échouée ({resp.status_code}): {detail}")

    return resp.json()

def is_paypal_capture_successful(capture_resp):
    """
    Retourne True si la capture PayPal contient au moins une capture 'COMPLETED'.
    """
    if not isinstance(capture_resp, dict):
        return False
    if capture_resp.get("status") == "COMPLETED":
        return True
    for pu in capture_resp.get("purchase_units", []):
        payments = pu.get("payments", {}) or {}
        for cap in payments.get("captures", []) or []:
            if cap.get("status") == "COMPLETED":
                return True
    return False
