from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import datetime
# splite3をimportする
# flaskをimportしてflaskを使えるようにする
# appにFlaskを定義して使えるようにしています。Flask クラスのインスタンスを作って、 app という変数に代入しています。

# appという名前でFlaskを使いますよ
app = Flask(__name__)
# secret key を設定
app.secret_key = "sunabaco"

@app.route("/")
def top_picture():
    # dbtest.dbに接続
    conn = sqlite3.connect("mappin_good.db")
    # データベースの中身が見えるようにする
    c = conn.cursor()
    # sqlを実行する
    # ここのピクチャーidは手動で変更
    c.execute("select user_id,picture,comment,time from picture where picture_id =1")
    # fetchoneはタプル型
    top_img = c.fetchone()
    print(top_img)
    
    c.execute("select picture,comment,picture_id from picture order by time desc ")
    new_imgs = c.fetchmany(size=4)

    c.execute("select site_name from site")
    site_name = c.fetchall()

    c.execute("select site_name,site_point from site order by site_point desc")
    site_point = c.fetchall()

    # 接続終了
    c.close()
    # 接続終了
    return render_template("index.html", top_img=top_img,new_imgs=new_imgs, site_name=site_name,site_point=site_point)


@app.route("/login",methods=["GET"])
def login_get():
    if "user_id" in session:
        return redirect("/user_page")
    else:
        return render_template("login.html")

@app.route("/login",methods=["POST"])
def login_post():
    # 入力フォームから値を取得
    name = request.form.get("name")
    password = request.form.get("password")
    # dbtest.dbに接続
    conn = sqlite3.connect("mappin_good.db")
    # データベースの中身が見れるようにする
    c = conn.cursor()
    # SQL文を実行する
    c.execute("select user_id from users where username=? and password=?",(name,password))

    user_id = c.fetchone()
    #IDが取得できているのかの確認
    print(user_id)
    # 接続終了
    c.close()

    if user_id is None:
        return redirect("/login")
    else:
        session["user_id"] = user_id
        return redirect("/user_page")


@app.route("/register",methods=["GET"])
def regist_get():
    if "user_id" in session:
        return redirect("/user_page")
    else:
        return render_template("register.html")


@app.route("/register",methods=["POST"])
def regist_post():
    # 入力フォームから値を取得
    name = request.form.get("name")
    password = request.form.get("password")
    site_name = request.form.get("site_name")
    nickname = request.form.get("nickname")
    # dbtest.dbに接続
    conn = sqlite3.connect("mappin_good.db")
    # データベースの中身が見れるようにする
    c = conn.cursor()
    # SQL文を実行する
    c.execute("insert into users values(null,?,?,?,?)",(name,password,nickname,site_name))
    # 変更を適用
    conn.commit()
    # 接続終了
    c.close()
    return redirect("/login")


# login状態でないと見れないページには、
# if "user_id" in session:
#        return 
#    else:
#        return 
# でその動作部分全体を囲ってあげる

@app.route("/user_page")
def greet():
    if "user_id" in session:
        user_id = session["user_id"][0]
        print(user_id)
        conn = sqlite3.connect("mappin_good.db")
        c = conn.cursor()
        c.execute("select nickname from users where user_id=?",(user_id,))
        nickname = c.fetchone()
        nickname = nickname[0]
        print(nickname)

        c.execute(
                "select * from picture where user_id = ? order by time desc ", (user_id,))
        my_list = []
        for row in c.fetchall():
            my_list.append({"picture_id": row[0], "user_id": row[1], "comment": row[2], "picture": row[3],
                                "time": row[4], "location_no": row[5], "good_count": row[6], "site_name": row[7], "junru_name": row[8], })

        c.close()
        return render_template("/user_page.html",nickname = nickname,my_list=my_list)
    else:
        return render_template("login.html")

@app.route("/edit")
def edit():
    if "user_id" in session:
        user_id = session["user_id"][0]
        print(user_id)
        conn = sqlite3.connect("mappin_good.db")
        c = conn.cursor()
        c.execute("select * from users where user_id=?",(user_id,))
        name_edit = c.fetchone()
        nickname = name_edit[3]
        print(nickname)
        c.close()
        return render_template("edit.html",nickname = nickname)
    else:
        return render_template("login.html")


@app.route("/upload", methods=["POST"])
def do_upload():
    # bbs.tplのinputタグ name="upload" をgetしてくる
    upload = request.files["upload"]
    # uploadで取得したファイル名をlower()で全部小文字にして、ファイルの最後尾の拡張子が'.png', '.jpg', '.jpeg'ではない場合、returnさせる。
    if not upload.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        return "png,jpg,jpeg形式のファイルを選択してください"
    # 下の def get_save_path()関数を使用して "./static/img/" パスを戻り値として取得する。
    save_path = get_save_path()
    # パスが取得できているか確認
    print(save_path)
    # ファイルネームをfilename変数に代入
    filename = upload.filename
    # 画像ファイルを./static/imgフォルダに保存。 os.path.join()は、パスとファイル名をつないで返してくれます。
    upload.save(os.path.join(save_path,filename))
    # ファイル名が取れることを確認、あとで使うよ
    print(filename)
    
    # アップロードしたユーザのIDを取得
    user_id = session["user_id"][0]
    comment = request.form.get("comment")
    time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    kouku = request.form.get("kouku")
    junru = request.form.get("junru")
    print(kouku)
    print(junru)
    conn = sqlite3.connect("mappin_good.db")
    c = conn.cursor()
    # update文
    # 上記の filename 変数ここで使うよ
    c.execute("insert into picture values(null,?,?,?,?,null,null,?,?)",(user_id,comment,filename,time,kouku,junru))
    conn.commit()
    conn.close()

    return redirect ("/user_page")

#課題4の答えはここも
def get_save_path():
    path_dir = "static/img"
    return path_dir 

@app.route("/logout", methods=["GET"])
def logout():
    #セッションからユーザ名を取り除く (ログアウトの状態にする)
    session.pop("user_id", None)
    # ログインページにリダイレクトする
    return redirect("/")

@app.route('/junru/<string:junru>')
def brows(junru):
    conn = sqlite3.connect('mappin_good.db')
    c = conn.cursor()
    print(junru)
    c.execute(
        "select * from picture where junru_name = ? order by time desc", (junru,))
    brows_list = []
    for row in c.fetchall():
        brows_list.append({"picture_id": row[0], "user_id": row[1], "comment": row[2], "picture": row[3],
                           "time": row[4], "location_no": row[5], "good_count": row[6], "site_name": row[7], "junru_name": row[8], })
    c.close()
    print(brows_list)
    return render_template("browsing_junru.html", junru=junru, brows_list=brows_list)


@app.route('/kouku/<string:kouku>')
def brows_kouku(kouku):
    conn = sqlite3.connect('mappin_good.db')
    c = conn.cursor()
    print(kouku)
    c.execute(
        "select * from picture  where site_name = ? order by time desc", (kouku,))
    brows_list = []
    for row in c.fetchall():
        brows_list.append({"picture_id": row[0], "user_id": row[1], "comment": row[2], "picture": row[3],
                           "time": row[4], "location_no": row[5], "good_count": row[6], "site_name": row[7], "junru_name": row[8], })
    c.close()
    print(brows_list)
    return render_template("browsing_kouku.html", kouku=kouku, brows_list=brows_list)

@app.route('/personal_page/<int:user_id>')
def brows_person(user_id):
    conn = sqlite3.connect('mappin_good.db')
    c = conn.cursor()
    
    c.execute(
        "select * from picture where user_id = ? order by time desc ", (user_id,))
    brows_list = []
    for row in c.fetchall():
        brows_list.append({"picture_id": row[0], "user_id": row[1], "comment": row[2], "picture": row[3],
                           "time": row[4], "location_no": row[5], "good_count": row[6], "site_name": row[7], "junru_name": row[8], })
    
    c.execute("select nickname,site_name from users where user_id = ? ", (user_id,))
    profile=c.fetchall()
    c.close()
    print(profile)
    return render_template("personal_page.html", brows_list=brows_list, profile=profile)

@app.route('/picture/<int:picture_id>')
def picture(picture_id):
    conn = sqlite3.connect('mappin_good.db')
    c = conn.cursor()
    print(picture_id)
    c.execute("select * from picture where picture_id = ? ", (picture_id,))
    img_profile=c.fetchall()

    c.execute("select nickname,site_name,user_id from users where user_id = ? ", (img_profile[0][1],))
    name=c.fetchall()
    c.close()
    return render_template("picture.html", img_profile=img_profile,name=name)





if __name__ == "__main__":
    app.run(debug=True)
