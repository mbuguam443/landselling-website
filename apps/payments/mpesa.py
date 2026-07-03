import json
import requests
from base64 import b64encode
from datetime import datetime
from django.conf import settings
from django.utils import timezone


def get_base_url():
    return getattr(settings, 'MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke')


def get_auth_token():
    """
    Get OAuth token from Safaricom Daraja API.
    Returns a simulated token when credentials are not configured.
    """
    consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', None)
    consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', None)

    if not consumer_key or not consumer_secret:
        return 'SIMULATED_TOKEN_' + datetime.now().strftime('%Y%m%d%H%M%S')

    base = get_base_url()
    api_url = f'{base}/oauth/v1/generate?grant_type=client_credentials'
    try:
        response = requests.get(
            api_url,
            headers={'Authorization': 'Basic ' + b64encode(
                f'{consumer_key}:{consumer_secret}'.encode()
            ).decode()}
        )
        return response.json().get('access_token', '')
    except Exception:
        return 'SIMULATED_TOKEN_' + datetime.now().strftime('%Y%m%d%H%M%S')


def stk_push(phone_number, amount, account_ref, transaction_desc='Land Payment'):
    """
    Initiate STK Push (Lipa Na M-Pesa Online).
    In dev mode without credentials, simulates a successful push.

    Returns: dict with ResponseCode, CheckoutRequestID, MerchantRequestID, etc.
    """
    consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', None)
    consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', None)
    passkey = getattr(settings, 'MPESA_PASSKEY', None)
    shortcode = getattr(settings, 'MPESA_SHORTCODE', '174379')
    callback_url = getattr(settings, 'MPESA_CALLBACK_URL',
                           'https://6248-102-205-50-218.ngrok-free.app/payments/mpesa/callback/')

    try:
        from apps.settings.models import CompanySetting
        cs = CompanySetting.objects.first()
        if cs and cs.mpesa_callback_url:
            callback_url = cs.mpesa_callback_url
    except Exception:
        pass

    is_simulation = not (consumer_key and consumer_secret and passkey)

    if is_simulation:
        from uuid import uuid4
        return {
            'MerchantRequestID': str(uuid4()),
            'CheckoutRequestID': 'ws_CO_' + datetime.now().strftime('%Y%m%d%H%M%S'),
            'ResponseCode': '0',
            'ResponseDescription': 'Success. Request accepted for processing',
            'CustomerMessage': 'Success. Request accepted for processing',
            '_simulated': True,
        }

    token = get_auth_token()
    if token.startswith('SIMULATED_'):
        return stk_push(phone_number, amount, account_ref, transaction_desc)

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = b64encode(
        (shortcode + passkey + timestamp).encode()
    ).decode()

    phone = phone_number.strip()
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('+'):
        phone = phone[1:]
    elif not phone.startswith('254'):
        phone = '254' + phone

    payload = {
        'BusinessShortCode': shortcode,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': int(round(float(amount))),
        'PartyA': phone,
        'PartyB': shortcode,
        'PhoneNumber': phone,
        'CallBackURL': callback_url,
        'AccountReference': account_ref[:12] if account_ref else 'LAND',
        'TransactionDesc': transaction_desc[:13] if transaction_desc else 'Land Payment',
    }

    try:
        base = get_base_url()
        response = requests.post(
            f'{base}/mpesa/stkpush/v1/processrequest',
            json=payload,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            }
        )
        return response.json()
    except Exception as e:
        return {
            'ResponseCode': '1',
            'ResponseDescription': str(e),
            'errorMessage': str(e),
        }


def query_stk_status(checkout_request_id):
    """
    Query the status of an STK Push transaction via Safaricom API.
    Useful when the callback was not received (e.g. ngrok down).

    Returns: dict with ResponseCode, ResultDesc, and optionally
             ResultCode from the query response.
    """
    consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', None)
    consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', None)
    passkey = getattr(settings, 'MPESA_PASSKEY', None)
    shortcode = getattr(settings, 'MPESA_SHORTCODE', '174379')

    is_simulation = not (consumer_key and consumer_secret and passkey)

    if is_simulation:
        return {
            'ResponseCode': '0',
            'ResponseDescription': 'Success',
            'ResultCode': '0',
            'ResultDesc': 'The service request has been processed successfully',
        }

    token = get_auth_token()
    if token.startswith('SIMULATED_'):
        return {
            'ResponseCode': '1',
            'ResponseDescription': 'Cannot query in simulation mode',
            'ResultCode': '1',
            'ResultDesc': 'Authentication failed',
        }

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = b64encode(
        (shortcode + passkey + timestamp).encode()
    ).decode()

    payload = {
        'BusinessShortCode': shortcode,
        'Password': password,
        'Timestamp': timestamp,
        'CheckoutRequestID': checkout_request_id,
    }

    try:
        base = get_base_url()
        response = requests.post(
            f'{base}/mpesa/stkpushquery/v1/query',
            json=payload,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            }
        )
        return response.json()
    except Exception as e:
        return {
            'ResponseCode': '1',
            'ResponseDescription': str(e),
            'ResultCode': '1',
            'ResultDesc': str(e),
        }


def simulate_callback(checkout_request_id, result_code='0', result_desc='Success'):
    """
    Build a simulated callback payload for dev/testing.
    """
    return {
        'Body': {
            'stkCallback': {
                'MerchantRequestID': checkout_request_id,
                'CheckoutRequestID': checkout_request_id,
                'ResultCode': result_code,
                'ResultDesc': result_desc,
                'CallbackMetadata': {
                    'Item': [
                        {'Name': 'Amount', 'Value': None},
                        {'Name': 'MpesaReceiptNumber', 'Value': 'SIM' + datetime.now().strftime('%y%m%d%H%M%S')},
                        {'Name': 'TransactionDate', 'Value': datetime.now().strftime('%Y%m%d%H%M%S')},
                        {'Name': 'PhoneNumber', 'Value': '254700000000'},
                    ]
                }
            }
        }
    }
