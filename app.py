from flask import Flask, request, redirect, render_template, current_app, abort
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


@app.route('/', methods=['GET'])
def index_page():
    return render_template('app.html')


@app.route('/', methods=['POST'])
def vk_auth():
    try:
        form_data = dict(request.form)
        cp = f'&captcha_sid={form_data["c_sid"][0]}&captcha_key={form_data["c_key"][0]}' if 'send_captcha' in form_data else ''
        form_data = ast.literal_eval(request.form['auth_data']) if 'c_sid' in form_data else form_data
        if 'auth_vk' in form_data:
            scopes = ','.join([str(i) for i in form_data['scope']]) if 'scope' in form_data else 'null'
            vkapp = apps[form_data["app_name"][0]]
            auth_resp = requests.get(
                f'https://oauth.vk.com/token?grant_type=password&scope={scopes}&client_id={vkapp["client_id"]}&client_secret={vkapp["client_secret"]}'
                f'&username={form_data["login"][0]}&password={form_data["pass"][0]}{cp}').json()
            if 'access_token' in auth_resp:
                getu_resp = requests.get(f'https://api.vk.com/method/users.get?user_id={auth_resp["user_id"]}&fields=photo_50').json()['response'][0]
                return render_template('success.html', token=auth_resp['access_token'], uid=auth_resp['user_id'], temp=scopes,
                                       name=f'{getu_resp["first_name"]} {getu_resp["last_name"]}', photo=getu_resp["photo_50"], appname=vkapp)
            elif 'error' in auth_resp:
                if 'captcha_sid' in auth_resp:
                    return render_template('captcha.html', c_sid=auth_resp['captcha_sid'], c_img=auth_resp['captcha_img'], auth_data=form_data)
                if 'error_description' in auth_resp:
                    return render_template('error.html', err_name=auth_resp['error'], err_desc=auth_resp['error_description'])
    except Exception as excp:
        return f'¯\_(ツ)_/¯ <br> {excp}'


def web_process():
    if __name__ == '__main__':
        app.jinja_env.line_statement_prefix = '%'
        app.jinja_env.add_extension('jinja2.ext.do')
        app.run(debug=True, host=os.environ.get('address', '0.0.0.0'), port=int(os.environ.get('PORT', 80)))


flask_thread = threading.Thread(target=web_process())
flask_thread.start()
