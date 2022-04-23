import datetime
import webbrowser
import requests
from flask import Flask, render_template, request, redirect, session
from data import db_session
from data.users import User
from data.items import Item


app = Flask(__name__)
app.config["SECRET_KEY"] = "Shop_X"
image = "http://ssl.gstatic.com/accounts/ui/avatar_2x.png"
lst = ["Сначала_новые", "Сначала_старые", "Цена_▼", "Цена_▲"]
lst1 = ["on", "off"]
op = ["y", "n"]
host = "http://127.0.0.1:5000/"


def test(text):
    return True if text.replace("_", "").replace("@", "").isalnum() else False


def create(name, password, word, email):
    user = User()
    user.name = name
    user.password = password
    user.word = word
    user.email = email
    user.coins = 0
    user.address = 'Москва'
    user.image = image
    user.dels = ''
    user.card_number = 2345123412341234
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()


def choose(a, b, filt, table='user', par='non', text=''):
    db_sess = db_session.create_session()
    if filt == "name":
        try:
            return [i for i in db_sess.query(User).all() if
                    str(i.name).lower() == a.lower()][0]
        except IndexError:
            return False
    elif filt == "password":
        return db_sess.query(User).filter(User.password == a).first()
    elif filt == "all":
        if table == 'user':
            return db_sess.query(User).all()
        else:
            if par == 'non':
                return [i for i in db_sess.query(Item).all()]
            if par == 'one':
                a = [i for i in db_sess.query(Item).all() if i.title == a]
                return a if a else None
            elif par == 'Сначала_новые' or par == 'Сначала_старые':
                if text == '':
                    return [i for i in db_sess.query(Item).all()]

                else:
                    return [i for i in db_sess.query(Item).all() if
                            text.lower() in str(i.title).lower()]
            elif par == 'Цена_▲' or par == 'Цена_▼':
                if text == '':
                    return [i for i in
                            db_sess.query(Item).order_by(Item.cost).all()]
                else:
                    return [i for i in
                            db_sess.query(Item).order_by(Item.cost).all() if
                            text.lower() in str(i.title).lower()]
    return any(True for i in db_sess.query(User).all() if
               str(i.name).lower() == a.lower() and User.password == b)


def edit(name, word, password):
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(
            User.name == name and User.word == word).first():
        user = db_sess.query(User).filter(User.name == name).first()
        user.password = password
        db_sess.commit()


def log(name):
    name = choose(name, '', 'name').name
    if 'nick' in session:
        session['nick'] = name
    else:
        session['nick'] = name


def whoami():
    return session['nick'] if 'nick' in session else False


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "GET":
        name = whoami() if whoami() else '%name'
        items = []
        items2 = []
        for i in choose('', None, "all", 'item', 'Сначала_новые')[::-1]:
            a = i.title if len(i.title) <= 8 else str(i.title)[:5] + ".."
            if len(items) == 10:
                break
            items.append([a, host + "static/images/" + str(
                              i.image), i.cost])
        for i in choose('', None, "all", 'item', 'Цена_▲'):
            a = i.title if len(i.title) <= 8 else str(i.title)[:5] + ".."
            if len(items2) == 10:
                break
            items2.append([a, host + "static/images/" + str(
                               i.image), i.cost])
        if not items:
            items.append(['Товаров не найдено', '', ''])
        if not items2:
            items2.append(['Товаров не найдено', '', ''])
        return render_template('main.html', nam=name, data1=items, data2=items2)
    elif request.method == "POST":
        a = request.form['sear'] if request.form['sear'] else "%"
        return redirect(host + "search/" + a, code=302)


@app.route('/logout')
def logt():
    session.pop('nick', None)
    return redirect(host + "", code=302)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    elif request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        for i in request.form.items():
            if not test(i[1]):
                if i[0] != 'email':
                    return render_template('register.html', error="Html",
                                       name=request.form['name'],
                                       email=request.form['email'],
                                       word=request.form['word'],
                                       passw=request.form['password'],
                                       con=request.form['confirm'])

        if choose(request.form['name'], "", "name"):
            return render_template('register.html', error="User",
                                   email=request.form['email'],
                                   word=request.form['word'],
                                   passw=request.form['password'],
                                   con=request.form['confirm'])
        elif request.form['password'] != request.form['confirm']:
            return render_template('register.html', error="Pass",
                                   name=request.form['name'],
                                   email=request.form['email'],
                                   word=request.form['word'],
                                   passw=request.form['password'])
        else:
            create(request.form['name'], request.form['password'],
                   request.form['word'],
                   request.form['email'])
            log(str(request.form['name']))
            return redirect("http://127.0.0.1:5000", code=302)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    elif request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        for i in request.form.items():
            if i[0] != 'email':
                if not test(i[1]):
                    return render_template('login.html', error="Html",
                                           name=request.form['name'],
                                           passw=request.form['password'])
        if not choose(request.form['name'], "", "name"):
            return render_template('login.html', error="User",
                                   passw=request.form['password'])
        elif not choose(request.form['password'], "", "password"):
            return render_template('login.html', error="Pass",
                                   name=request.form['name'])
        else:
            log(request.form['name'])
            try:
                if request.form['rem']:
                    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
            except KeyError:
                pass
            return redirect(host + "", code=302)


@app.errorhandler(404)
def Page(error):
    return render_template("page404.html", title='Страница не найдена')


@app.route('/forgot', methods=['POST', 'GET'])
def forgot():
    if whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    elif request.method == 'GET':
        return render_template('forgot.html')
    elif request.method == 'POST':
        a = choose(request.form['name'], "", "name")
        if a:
            for i in request.form.items():
                if i[0] != 'button':
                    if not test(i[1]):
                        return render_template('forgot.html', error="Html",
                                               word=request.form['word'],
                                               new=request.form['new'])
        if not a:
            return render_template('forgot.html', error="User",
                                   word=request.form['word'],
                                   new=request.form['new'])
        elif a.word != request.form['word']:
            return render_template('forgot.html', error="Word",
                                   name=request.form['name'],
                                   new=request.form['new'])
        else:
            edit(request.form['name'], request.form['word'],
                 request.form['new'])
            log(str(request.form['name']))
            return redirect("http://127.0.0.1:5000", code=302)


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    else:
        items = []
        for i in choose('', None, "all", 'item'):
            if whoami() in i.cart:
                items.append([i.title,
                              host + "static/images/" + str(
                                  i.image), i.cost])
        num1 = len(items)
        items = []
        for i in choose('', None, "all"):
            if whoami() == i.name:
                a = i.dels.split()
                for j in range(len(a)):
                    k = 0
                    if j % 2 == 0:
                        b = str(a[j + 1]) + ' days' if str(
                            a[j + 1]) == '1' else str(a[j + 1]) + ' day'
                        items.append(
                            ['', host + "static/images/" + a[j],
                             b])
                        k += 1
                break
        num2 = len(items)
        items = []
        for i in choose('', None, "all", 'item'):
            if whoami() == i.seller:
                items.append(
                    [i.title, host + "static/images/" + i.image,
                     i.cost])
        num3 = len(items)
        if request.method == 'GET':
            if choose(whoami(), None, 'name'):
                al = choose(whoami(), "", "name")
                im = image if not al else al.image
                return render_template('profile.html', name=al.name,
                                       passw=al.password, address=al.address,
                                       email=al.email, image=im, user=al.name,
                                       num1=num1, num2=num2, num3=num3)
            else:
                redirect(host + "login", code=302)
        elif request.method == 'POST':
            try:
                file = request.files['file']
                file_name = file.filename
                file.save(f'static/images/{str(file_name)}')
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.name == whoami()).first()
                user.image = f'http://127.0.0.1:5000/static/images/{str(file_name)}'
                db_sess.commit()
            except KeyError:
                if choose(whoami(), None, "name"):
                    db_sess = db_session.create_session()
                    user = db_sess.query(User).filter(User.name == whoami()).first()
                    user.password = request.form['password']
                    user.address = request.form['address']
                    user.email = request.form['email']
                    db_sess.commit()
            al = choose(whoami(), "", "name")
            im = image if not al else al.image
            return render_template('profile.html', name=al.name,
                                   passw=al.password, address=al.address,
                                   email=al.email, image=im, user=al.name,
                                   num1=num1, num2=num2, num3=num3)


@app.route("/cart")
def cart():
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    items = []
    for i in choose('', None, "all", 'item'):
        if whoami() in i.cart:
            items.append([i.title,
                          host + "static/images/" + str(
                              i.image), i.cost])
    if not items:
        items.append(['Товаров не найдено', '', ''])
    return render_template("base.html", title="Cart", data=items,
                           head='Корзина:')


@app.route("/dels")
def dels():
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    items = []
    for i in choose('', None, "all"):
        if whoami() == i.name:
            a = i.dels.split()
            for j in range(len(a)):
                k = 0
                if j % 2 == 0:
                    b = str(a[j + 1]) + ' days' if str(
                        a[j + 1]) == '1' else str(a[j + 1]) + ' day'
                    items.append(
                        ['', host + "static/images/" + a[j],
                         b])
                    k += 1
            break
    if not items:
        items.append(['Товаров не найдено', '', ''])
    return render_template("base.html", title="Shipping", data=items,
                           head='В доставке:')


@app.route("/items")
def it():
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    items = []
    for i in choose('', None, "all", 'item'):
        if whoami() == i.seller:
            items.append(
                [i.title, host + "static/images/" + i.image,
                 i.cost])
    if not items:
        items.append(['Товаров не найдено', '', ''])
    return render_template("base.html", title="Goods", data=items,
                           head='Ваши товары:')


@app.route('/search/<word>', methods=['POST', 'GET'])
def search(word):
    if request.method == 'POST':
        a = request.form.getlist('fast')
        b = request.form.getlist('free')
        a = "&off" if not a else "&on"
        b = "&off&" if not b else "&on&"
        c = "" if not request.form['text'] else request.form['text']
        return redirect(host + "search/" + str(request.form['ord']) + a + b + str(c), code=302)
    elif request.method == 'GET':
        items = []
        if "&" in word:
            vals = [i for i in word.split("&")]
        else:
            word = '' if word == '%' else word
            vals = ['Сначала новые', 'off', 'off', word]
        if not 3 < len(vals) <= 4 or vals[0] not in lst or vals[1] not in lst1 or vals[2] not in lst1 or\
                (not test(vals[3]) and vals[3] != ''):
            return redirect(host + "search/Сначала_новые&off&off&", code=302)
        else:
            item = choose('', None, "all", 'item', vals[0], vals[3])
            for i in item:
                if ((vals[1] == i.fast) or vals[1] == "off") and ((vals[2] == i.free) or vals[2] == "off"):
                    items.append([i.title,
                                  host + "static/images/" + i.image,
                                  i.cost])
            if vals[0] == 'Сначала_новые' or vals[0] == 'Цена_▼':
                items = items[::-1]
            if not items:
                items.append(['Товаров не найдено', '', ''])
            return render_template('search.html', data=items, vals=vals)


@app.route("/item/<name>")
def show(name):
    i = choose(name, '', 'all', 'item', 'one')[0]
    if not i:
        return redirect(host + "LOL_stop_trying", code=302)
    else:
        return render_template('item.html', image=host + "static/images/" + i.image, seller=i.seller,
                               name=i.title, cost=i.cost)


@app.route("/cart/<name>")
def sh(name):
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    else:
        n = whoami()
        db_sess = db_session.create_session()
        a = db_sess.query(Item).filter(Item.title == name).first()
        if a and n not in a.cart and whoami() != a.seller:
            a.cart += ' ' + whoami()
            db_sess.commit()
        return redirect(host + "", code=302)


@app.route("/uns/<name>")
def uns(name):
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    else:
        n = whoami()
        db_sess = db_session.create_session()
        a = db_sess.query(Item).filter(Item.title == name).first()
        if a and n in a.cart:
            a.cart = a.cart.replace(whoami(), '')
            db_sess.commit()
        elif a and whoami() == a.seller:
            db_sess = db_session.create_session()
            db_sess.delete(db_sess.query(Item).filter(Item.title == name).first())
            db_sess.commit()
        return redirect(host + "profile", code=302)


@app.route('/add', methods=['POST', 'GET'])
def addn():
    if request.method == 'GET':
        return render_template('cret.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        name = request.form['name']
        price = request.form['price']
        img = request.form['file1']
        fast = request.form['fast']
        free = request.form['free']
        file_name = request.form['file1']
        if fast.lower() in op and free.lower() in op and not db_sess.query(Item).filter(
                Item.title == name).first() and int(price) <= 9999:
            fast = 'on' if fast == 'y' else 'off'
            free = 'on' if fast == 'y' else 'off'
            return redirect(
                f"http://127.0.0.1:5000/add/{name.replace(' ', '_')}&{price}&{img}&{fast}&{free}",
                code=302)
        else:
            if [i for i in db_sess.query(Item).all() if str(i.title).lower() == name.lower()]:
                return render_template('cret.html', error='User',
                                       price=price, img=img, fast=fast,
                                       free=free, file_name=file_name, src=host + file_name)
            elif int(price) > 9999:
                return render_template('cret.html', error='Price',
                                       name=name,
                                       img=img, fast=fast, free=free, file_name=file_name, src=host + file_name)
            else:
                return render_template('cret.html', error='Yn',
                                       name=name, price=price,
                                       img=img, file_name=file_name, src=host + file_name)


@app.route("/add/<name>")
def ad(name):
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    else:
        n = whoami()
        db_sess = db_session.create_session()
        a = db_sess.query(Item).filter(Item.title == name).first()
        if not a:
            vals = name.split('&')
            item = Item()
            item.title = vals[0]
            item.cost = vals[1]
            item.seller = n
            item.cart = ' '
            item.image = vals[2]
            item.fast = vals[3]
            item.free = vals[4]
            db_sess.add(item)
            db_sess.commit()
        return redirect(host + "", code=302)


@app.route("/Nick")
def nick():
    return """
            <link rel="stylesheet"
            href="static\css\styles.css">
            <div class="text-effect">
            <body style="height: 100%; width: 100%; background-color: rgb(0, 0, 0);">
            <h1 class="neon" data-text="Nick">Nick</h1>
            <div class="gradient"></div>
            <div class="spotlight"></div>
            </div>
            </body>"""


@app.route('/pay50000')
def paing():
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    else:
        db_sess = db_session.create_session()
        a = [i for i in db_sess.query(User).all() if i.name == whoami()][0]
        if a:
            if not a.coins:
                a.coins = 0
            a.coins += 50000
            db_sess.commit()
        return redirect(host, code=302)


@app.route("/card")
def card():
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    else:
        url = "file:///C:/Users/user/PycharmProjects/Flask/templates/index.html"
        webbrowser.open(url)
        return redirect(host + 'profile', code=302)


@app.route("/buy/<name>")
def bu(name):
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    else:
        n = whoami()
        db_sess = db_session.create_session()
        a = [i for i in db_sess.query(Item).all() if i.title == name][0]
        b = [i for i in db_sess.query(User).all() if i.name == whoami()][0]
        if b and a and a.seller != n:
            time = "7" if a.fast == 'off' else "1"
            b.dels += ' ' + a.image + ' ' + time
            db_sess.delete(a)
            db_sess.commit()
        return redirect(host + "search/Сначала_новые&off&off&", code=302)


@app.route('/map')
def map():
    if not whoami():
        return redirect(host + "LOL_stop_trying", code=302)
    else:
        try:
            word = choose(whoami(), '', 'name').address
            word.replace('_', ', ')
            geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?" \
                               f"apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={word}&format=json"
            response = requests.get(geocoder_request)
            if response:
                json_response = response.json()
                toponym = \
                    json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                toponym_coodrinates = toponym["Point"]["pos"]
                lst = []
                strr = ''
                for i in toponym_coodrinates:
                    if i == ' ':
                        lst.append(strr)
                        strr = ''
                    else:
                        strr += i
                lst.append(strr)
                map_request = f"http://static-maps.yandex.ru/1.x/?ll={lst[0]},{lst[1]}&spn=0.002,0.002&l=sat"
                response = requests.get(map_request)
                map_file = 'static/map.png'
                with open(map_file, "wb") as file:
                    file.write(response.content)
                return render_template('map.html', src=host + "static/map.png", word=word)
            elif not response:
                return redirect("http://127.0.0.1:5000/wronaddress")
        except IndexError:
            return redirect("http://127.0.0.1:5000/wronaddress")


if __name__ == "__main__":
    db_session.global_init("db/users.db")
    db_session.global_init("db/items.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
