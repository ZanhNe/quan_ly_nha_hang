from .interface import ThanhToanOnline
from typing import Dict, Any
from dotenv import load_dotenv
import os
import stripe

load_dotenv()

class Stripe(ThanhToanOnline):

    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = os.getenv('SECRET_KEY')


    def xu_ly_thanh_toan_online(self, so_tien: int, metadata):
        try:
            intent = self.stripe.PaymentIntent.create(
            amount=int(so_tien),
            currency='vnd',
            metadata=metadata,
            automatic_payment_methods={
                'enabled': True
                }
            )
            return {'clientSecret': intent['client_secret']}
        except Exception as e:
            raise e
    

    def xac_thuc_webhook(self, payload, sig_header, endpoint_secret) -> Dict[str, Any]:
        event = None
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as err:
            raise Exception("Invalid Payload")
        except self.stripe.SignatureVerificationError as err:
            raise Exception("Invalid Signature")
        
        if event['type'] == 'payment_intent.succeeded':
            return event['data']['object']['metadata']
        else:
            raise Exception("Không phải sự kiện payment_intent.succeeded")
        
    