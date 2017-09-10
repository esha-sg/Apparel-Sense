import operator
import os
from random import shuffle
import pygal
from PIL import Image
from flask import json
from flask import session
from pygal.style import DarkSolarizedStyle
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from label_image import get_labels
from predict_attributes import get_tags
from similarity import get_similar_images, get_related_products
from flaskext.mysql import MySQL

app = Flask(__name__)

# Application Configurations
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SIM_IMG'] = "static/"
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'JPG'}

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'eshwarsg24'
app.config['MYSQL_DATABASE_DB'] = 'ECom'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.secret_key = '3#45iormdxsal'
mysql.init_app(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def home():
    if session.get('user'):
        o = ['Logout', str(session['username']) + '\'s A-Sense' + str('!')]
        return render_template('home.html', obj=o)
    else:
        return render_template('home.html')


@app.route('/index')
def index():
    if session.get('user'):
        o = ['Logout', 'Welcome ' + str(session['username']) + str('!')]
        return render_template('index.html', obj=o)
    else:
        return render_template('index.html')


@app.route('/showSignUp')
def showSignUp():
    return render_template('register.html')


@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        # validate the received values
        if _name and _email and _password:

            # All Good, let's call MySQL

            conn = mysql.connect()
            cursor = conn.cursor()
            # _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser', (_name, _email, _password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/showSignin')
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        o = ['Logout', 'Welcome ' + str(session['username']) + str('!')]
        return render_template('home.html', obj=o)
    else:
        return render_template('account.html')


@app.route('/userHome')
def userHome():
    if session.get('user'):
        o = ['Logout', 'Welcome ' + str(session['username']) + str('!')]
        return render_template('home.html', obj=o)
    else:
        return render_template('error.html', error='Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    return redirect('/')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin', (_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if str(data[0][3]) == _password:
                session['user'] = data[0][0]
                session['username'] = data[0][1]
                return redirect('/userHome')
            else:
                return render_template('error.html', error='Wrong Email address or Password.')
        else:
            return render_template('error.html', error='Wrong Email address or Password.')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/up', methods=['POST'])
def up():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        folder = "/home/eshwar/PycharmProjects/FlaskApp/static/"
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
        return redirect(url_for('uploaded_file', filename=filename))


@app.route('/show/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file', filename=filename))


@app.route('/show/<filename>')
def uploaded_file(filename):
    file = app.config['UPLOAD_FOLDER'] + filename
    predictions, bottleneck = get_labels(file)
    cnt = 0
    scores = []
    labels = []
    for i in predictions:
        cnt += 1
        if cnt % 2 == 0:
            scores.append(i)
        else:
            labels.append(i)

    bar_chart = pygal.Bar(width=600, height=300,
                          explicit_size=True, title="Classification Results",
                          style=DarkSolarizedStyle, disable_xml_declaration=True)
    bar_chart.x_labels = labels
    bar_chart.add('P(C)', scores)

    sim = get_similar_images(filename, labels[0], bottleneck)

    tags = [labels[0], round(scores[0] * 100, 2)]

    if labels[0] not in ['footwear', 'pants']:
        attributes = get_tags(file)
        tags = tags + attributes

    if session.get('user'):
        o = ['Logout', 'Welcome ' + str(session['username']) + str('!')]
        return render_template('products.html', filename=filename, pred=tags, bar_chart=bar_chart, similar_images=sim,
                               obj=o)
    else:
        return render_template('products.html', filename=filename, pred=tags, bar_chart=bar_chart, similar_images=sim)


@app.route('/showProducts/<name>')
def showProducts(name):
    image_list = '/home/eshwar/PycharmProjects/FlaskApp/static/data/' + name + '/'
    img_path = '/static/data/' + name + '/'
    cluster = os.listdir(image_list)
    images = []
    like_lis = {}
    check_arr = []
    for i in cluster:
        lis = os.listdir(image_list + i + '/')
        # shuffle(lis)
        for j in range(0, 6):
            str_path = img_path + i + '/' + lis[j]
            images.append(str_path)
            like_lis[str_path] = 0
        shuffle(images)
    if session.get('user'):
        con = mysql.connect()
        cursor = con.cursor()
        query = 'SELECT image_id, cluster from likes where user_id = %s AND class= \'%s\'' % (session['user'], name)
        number = cursor.execute(query)
        rs = cursor.fetchall()
        product_recommendation = {}
        recommend_images = []
        if number > 0:
            for i in range(0, number):
                like_lis[rs[i][0]] = 1

                if rs[i][1] not in product_recommendation:
                    product_recommendation[rs[i][1]] = {}
                    product_recommendation[rs[i][1]] = 1
                else:
                    product_recommendation[rs[i][1]] += 1
            cluster_affinity = max(product_recommendation.items(), key=operator.itemgetter(1))[0]
            recommend_images = os.listdir(image_list + str(cluster_affinity) + '/')
            shuffle(recommend_images)
            recommend_images = recommend_images[0:10]
            for i in range(0, len(recommend_images)):
                recommend_images[i] = img_path + str(cluster_affinity) + '/' + recommend_images[i]

        for i in images:
            if like_lis[i] == 1:
                check_arr.append(1)
            else:
                check_arr.append(0)
    else:
        for i in range(0, len(images)):
            check_arr.append(0)
        recommend_images = []

    length = len(images)
    if session.get('user'):
        o = ['Logout', str(session['username'])+'\'s A-Sense' + str('!')]
        return render_template('display.html', lis=images, check_arr=check_arr, len=length,
                               recommended_list=recommend_images, obj=o)
    else:
        return render_template('display.html', lis=images, check_arr=check_arr, len=length,
                               recommended_list=recommend_images)


@app.route('/showSingle', methods=['GET'])
def showSingle():
    val = request.args['value']
    info = val.split('/')
    class_label = info[3]
    cluster = info[4]
    name = info[5] + '.txt'
    related_product_list = get_related_products(class_label, cluster, name)
    tags = [class_label]
    if class_label not in ['footwear', 'pants']:
        attributes = get_tags(str(val))
        tags += attributes
    im = Image.open('/home/eshwar/PycharmProjects/FlaskApp/' + val)
    pix = im.load()
    width, height = im.size
    color = pix[width / 2, height / 2]
    # color = im.resize((1, 1), Image.ANTIALIAS).getpixel((0, 0))
    if session.get('user'):
        o = ['Logout', 'Welcome ' + str(session['username']) + str('!')]
        return render_template('single.html', image=val, tags=tags, related_products=related_product_list, obj=o,
                               color=color)
    else:
        return render_template('single.html', image=val, tags=tags, related_products=related_product_list, color=color)


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route('/like', methods=['POST'])
def like():
    img_id = request.json['theid']
    temp = img_id.split('/')
    class_label = temp[3]
    cluster = temp[4]
    if session.get('user'):
        con = mysql.connect()
        cursor = con.cursor()

        query = 'INSERT INTO likes (user_id, image_id, class, cluster) VALUES (%s, \'%s\', \'%s\', %s)' % (
            session['user'], img_id, class_label, cluster)
        cursor.execute(query)
        con.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 401, {'ContentType': 'application/json'}


@app.route('/unlike', methods=['POST'])
def unlike():
    img_id = request.json['theid']
    if session.get('user'):
        con = mysql.connect()
        cursor = con.cursor()
        query = 'DELETE FROM likes WHERE `user_id` = %s AND `image_id` = \'%s\'' % (session['user'], img_id)
        cursor.execute(query)
        con.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 401, {'ContentType': 'application/json'}

@app.route('/yourEstop')
def recommend():
    if session.get('user'):
        con = mysql.connect()
        cursor = con.cursor()
        query = 'SELECT image_id FROM likes WHERE `user_id` = %s' % (session['user'])
        number = cursor.execute(query)
        rs = cursor.fetchall()
        rec = []
        for i in range(0, number):
            q = 'SELECT first, second, third FROM similar WHERE `image_id` = \'%s\'' % (rs[i][0])
            cursor.execute(q)
            r = cursor.fetchall()
            for i in range(0, 2):
                rec.append(r[0][i])
        con.commit()
        shuffle(rec)
        o = ['Logout', 'Welcome ' + str(session['username']) + str('!')]

        return render_template('foryou.html', rec_images=rec, obj=o)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == '__main__':
    app.run()
