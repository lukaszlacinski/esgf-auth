from django.shortcuts import render
from social_django.utils import load_strategy

def demo(request):

    uid = None
    access_token = None
    refresh_token = None
    other_tokens = None
    cert = None
    key = None
    cn = None

    if request.user.is_authenticated():
        social = request.user.social_auth.get(provider='esgf')
        uid = social.uid
        access_token = social.extra_data['access_token']
        refresh_token = social.extra_data['refresh_token']
        print dir(social)

        strategy = load_strategy()
        backend = social.get_backend_instance(strategy)
        key, cert, cn = backend.get_certificate(access_token)


    return render(request,
            'auth/demo.html', {
                'uid': uid,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'certificate': cert,
                'private_key': key,
                'common_name': cn
            })
