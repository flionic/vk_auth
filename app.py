from flask import Flask, request, redirect, render_template, current_app, abort, jsonify, session
import requests
import os
import threading
import ast

apps = {'android': {'client_id': '2274003', 'client_secret': 'hHbZxrka2uZ6jB1inYsH'},
        'iphone': {'client_id': '3140623', 'client_secret': 'VeWdmVclDCtn6ihuP1nt'},
        'ipad': {'client_id': '3682744', 'client_secret': 'mY6CDUswIVdJLCD3j15n'},
        'windowsphone': {'client_id': '3502557', 'client_secret': 'PEObAuQi6KloPM4T30DV'},
        'windows': {'client_id': '3697615', 'client_secret': 'AlVXZFMUqyrnABp8ncuU'}}

app = Flask(__name__)

@app.route('/auth')
def auth_vk():
    if len(request.args) == 0:
        return abort(403)
    try:
        print(dict(request.args))
        form_data = dict(request.args)
        cp = f'&captcha_sid={form_data["c_sid"][0]}&captcha_key={form_data["c_key"][0]}' if 'send_captcha' in form_data else ''
        twofa = f'&2fa_supported=1&code={form_data["code"][0]}' if ('code' in form_data) and (len(form_data['code']) > 0) else ''
        print(f'2fa {twofa}')
        form_data = ast.literal_eval(request.form['auth_data']) if 'c_sid' in form_data else form_data
        session['vk_login'] = form_data["login"][0]
        scopes = ','.join([str(i) for i in form_data['scope']]) if 'scope' in form_data else 'null'
        vkapp = apps[form_data["app_name"][0]]
        auth_resp = requests.get(
            f'https://oauth.vk.com/token?grant_type=password&scope={scopes}&client_id={vkapp["client_id"]}&client_secret={vkapp["client_secret"]}'
            f'&username={form_data["login"][0]}&password={form_data["pass"][0]}{cp}{twofa}').json()
        print(f'https://oauth.vk.com/token?grant_type=password&scope={scopes}&client_id={vkapp["client_id"]}&client_secret={vkapp["client_secret"]}'
            f'&username={form_data["login"][0]}&password={form_data["pass"][0]}{cp}{twofa}')
        if 'access_token' in auth_resp:
            getu_resp = requests.get(f'https://api.vk.com/method/users.get?user_id={auth_resp["user_id"]}&fields=photo_50').json()['response'][0]
            return jsonify(status=1, token=auth_resp['access_token'], uid=auth_resp['user_id'], temp=scopes,
                                   name=f'{getu_resp["first_name"]} {getu_resp["last_name"]}', photo=getu_resp["photo_50"])
        elif 'error' in auth_resp:
            print(auth_resp)
            if 'invalid_client' in auth_resp['error']:
                return jsonify(status=2)
            if 'need_validation' in auth_resp['error']:
                return jsonify(status=3)
            if 'invalid_request' in auth_resp['error'] and auth_resp['error_description'] == 'wrong code':
                return jsonify(status=4)
            if 'captcha_sid' in auth_resp:
                return jsonify(status=5, c_sid=auth_resp['captcha_sid'], c_img=auth_resp['captcha_img'], auth_data=form_data)
            if 'error_description' in auth_resp:
                return jsonify(status=6, err_name=auth_resp['error'], err_desc=auth_resp['error_description'])
    except Exception as excp:
        return jsonify(exception=excp)
    return abort(403)


@app.route('/app')
def index():
    return render_template('app_test.html')


@app.route('/', methods=['GET'])
def index_page():
    return render_template('app.html')


def web_process():
    if __name__ == '__main__':
        app.jinja_env.line_statement_prefix = '%'
        app.jinja_env.add_extension('jinja2.ext.do')
        app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
        app.run(debug=True, host=os.environ.get('address', '0.0.0.0'), port=int(os.environ.get('PORT', 80)))


flask_thread = threading.Thread(target=web_process())
flask_thread.start()
