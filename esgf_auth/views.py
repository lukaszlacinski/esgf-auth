from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from social_django.utils import load_strategy
from backends.esgf import discover
from urllib import urlencode


def demo(request):

    uid = None
    access_token = None
    refresh_token = None
    other_tokens = None
    cert = None
    key = None
    cn = None

    openid = request.GET.get('openid_identifier', None)

    if request.user.is_authenticated():
        social = None
        try:
            social = request.user.social_auth.get(provider='esgf')
            access_token = social.extra_data['access_token']
            refresh_token = social.extra_data['refresh_token']
            strategy = load_strategy()
            backend = social.get_backend_instance(strategy)
            key, cert, cn = backend.get_certificate(access_token)
        except Exception:
            pass

        try:
            social = request.user.social_auth.get(provider='esgf-openid')
        except Exception:
            pass

        uid = social.uid

    elif openid:
        protocol = discover(openid)
        if protocol:
            request.session['openid_identifier'] = openid
            request.session['next'] = request.GET.get('next', '/')
            if protocol == 'OpenID':
                return redirect(reverse('social:begin', args=['esgf-openid']))
            elif protocol == 'OAuth2':
                return redirect(reverse('social:begin', args=['esgf']))
        else:
            return render(request,
                    'auth/demo.html', {
                        'message': 'No OpenID/OAuth2/OIDC service discovered'
                    })

    return render(request,
            'auth/demo.html', {
                'uid': uid,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'certificate': cert,
                'private_key': key,
                'common_name': cn
            })
