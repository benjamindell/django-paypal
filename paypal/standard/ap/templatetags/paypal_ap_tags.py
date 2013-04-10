from django.conf import settings
from django import template

from paypal.standard.conf import *
from paypal.standard.ap.conf import *

import httplib, urllib, urlparse, sys

register = template.Library()

@register.inclusion_tag('paypal/adaptive_payment/button.html')
def paypal_adaptive_button(payment):
    #Set our headers
    headers = {
                'Content-type':'application/x-www-form-urlencoded',
                'Accept':'text/plain',
                'X-PAYPAL-SECURITY-USERID': settings.PAYPAL_API_USERNAME, 
                'X-PAYPAL-SECURITY-PASSWORD': settings.PAYPAL_API_PASSWORD, 
                'X-PAYPAL-SECURITY-SIGNATURE': settings.PAYPAL_API_SIGNATURE,
                'X-PAYPAL-APPLICATION-ID': settings.PAYPAL_API_APPLICATION_ID,
                'X-PAYPAL-REQUEST-DATA-FORMAT':'NV',
                'X-PAYPAL-RESPONSE-DATA-FORMAT':'NV'
                }
    
    params = {
        'actionType': 'CREATE',
        'requestEnvelope.detailLevel': 'ReturnAll',
        'requestEnvelope.errorLanguage': 'en_US',
        'feesPayer': 'EACHRECEIVER',
    }
    params.update(payment)
    options = params.pop('options', {})
    
    ### CREATE PAYMENT    
    enc_params = urllib.urlencode(params)
     
    conn = httplib.HTTPSConnection(SANDBOX_SVCS_ENDPOINT if settings.PAYPAL_TEST else SVCS_ENDPOINT)
    conn.request("POST", "/AdaptivePayments/Pay", enc_params, headers)
     
    response = conn.getresponse()
    data = urlparse.parse_qs(response.read())
    paykey = data.get('payKey', [None])[0]     
    conn.close()

    ### SET PAYMENT OPTIONS
    if paykey and options:
        options.update({
            'payKey': paykey,
            'requestEnvelope.errorLanguage': 'en_US',
            'requestEnvelope.detailLevel': 'ReturnAll',
        })
        enc_options = urllib.urlencode(options)
         
        conn = httplib.HTTPSConnection(SANDBOX_SVCS_ENDPOINT if settings.PAYPAL_TEST else SVCS_ENDPOINT)
        conn.request("POST", "/AdaptivePayments/SetPaymentOptions", enc_options, headers)
         
        response = conn.getresponse()
        data = urlparse.parse_qs(response.read())
        conn.close()
    
    url = SANDBOX_POSTBACK_ENDPOINT if settings.PAYPAL_TEST else POSTBACK_ENDPOINT

    if not paykey:
        sys.stderr.write('\nPayPal Error: \n%s \n\nHeaders:\n%s \n\nParams:\n%s \n\n' % (data, headers, params))
        sys.stderr.flush()
    
    return {
        'url': url,
        'image': SANDBOX_IMAGE if settings.PAYPAL_TEST else IMAGE,
        'paykey': paykey,
    }
    
