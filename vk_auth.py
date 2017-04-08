from flask import Flask, request, redirect, render_template
import requests
import os
import threading
import ast

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def handle_incoming_messages():
    excp = ''; scopes = ''
    try:
        if request.method == 'POST':
            form_data = dict(request.form)
            cp = f'&captcha_sid={form_data["c_sid"][0]}&captcha_key={form_data["c_key"][0]}' if 'send_captcha' in form_data else ''
            form_data = ast.literal_eval(request.form['auth_data']) if 'c_sid' in form_data else form_data
            if ('auth_vk' in form_data) and ('scope' in form_data):
                for i in form_data['scope']:
                    scopes += f'{i},'
                scopes = scopes[:-1]
                r = requests.get(f'https://oauth.vk.com/token?grant_type=password&scope={scopes}&client_id=2274003&client_secret=hHbZxrka2uZ6jB1inYsH'
                    f'&username={form_data["login"][0]}&password={form_data["pass"][0]}{cp}').json()
                if 'access_token' in r:
                    vku = requests.get(f'https://api.vk.com/method/users.get?user_id={r["user_id"]}&fields=photo_50').json()['response'][0]
                    return render_template('success.html', token=r['access_token'], uid=r['user_id'],
                                           name=f'{vku["first_name"]} {vku["last_name"]}', photo=f'{vku["photo_50"]}', temp=f'{scopes}')
                elif 'error' in r:
                    if 'captcha_sid' in r:
                        return render_template('captcha.html', c_sid=r['captcha_sid'], c_img=r['captcha_img'], auth_data=form_data)
                    if 'error_description' in r:
                        return render_template('error.html', err_name=r['error'], err_desc=r['error_description'])
    except Exception as r_ex:
        excp += f'e4: {r_ex}<br>'; print(excp)
        return f'Finally:<br><br>{excp}' if len(excp) > 0 else str(r)


def web_process():
    if __name__ == '__main__':
        app.run(debug=True, host=os.environ.get('address', '0.0.0.0'), port=int(os.environ.get('PORT', 80)))


flask_thread = threading.Thread(target=web_process())
flask_thread.start()
