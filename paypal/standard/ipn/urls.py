from django.conf.urls.defaults import *

urlpatterns = patterns('paypal.standard.ipn.views',            
    url(r'^$', 'ipn', name="paypal-ipn"),
    url(r'^ap/$', 'ap_ipn', name="paypal-ap-ipn"),
    #url(r'^mp/$', 'ap_ipn', name="paypal-mp-ipn"),
)