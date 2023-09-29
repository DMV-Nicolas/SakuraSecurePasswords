from flask import Flask, render_template, request, redirect, url_for, session, flash, escape, g, abort
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from functions import *
import os, re

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
db=SQLAlchemy(app)
mail=Mail(app)

#procesos de verificacion
class signup_procedure():
    def __init__(self,username,email,password,checkPassword):
        self.username=username
        self.email=email
        self.password=password
        self.checkPassword=checkPassword
        self.verify_email = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
        self.letters="abcdefghijklmnñopqrstuvwxyzABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
    def requeriments(self):
        for x in self.password:
            if (any(chr==x for chr in self.letters)):
                isletters=True
                break
            else:
                isletters=False
        if (self.username=="") or (self.email=="") or (self.password==""):
            return "Debes rellenar todos los campos"
        elif (len(self.username))<(3):
            return "El nombre de usuario debe tener un minimo de 3 caracteres"
        elif (len(self.password))<(12):
            return "La contraseña debe tener un minimo de 12 caracteres"
        elif  not (any(chr.isdigit() for chr in self.password)):
            return "La contraseña debe tener por lo menos 1 numero"
        elif not isletters:
            return "La contraseña debe tener por lo menos 1 letra"
        elif (self.password.islower()) or (self.password.isupper()):
            return "La contraseña debe contener por lo menos una mayuscula y una minuscula"
        elif not (re.match(self.verify_email, self.email)) is not None:
            return "Porfavor digitar un email valido"
        elif (Users_profile.query.filter_by(email=self.email).first()):
            return f"El email {self.email} ya existe"
        elif not (self.password==self.checkPassword):
            return "Las contraseñas no coinciden"
        else:
            return None
class add_procedure():
    def __init__(self,name,actualName,password):
        self.name=name
        self.actualName=actualName
        self.password=password
    def requeriments(self):
        accounts=[]
        user=Users_profile.query.filter_by(username=g.user).first()
        if user.accounts.all():
            accounts=user.accounts.order_by(Users_accounts.id).all()
            accountRegistered=False
            for x in accounts:
                if (x.name==self.name):
                    accountRegistered=True
                    break
            if (self.name=="") or (self.name.isspace()):
                return "El campo de nombre es requerido"
            elif (self.password.find("ñ")!=-1) or (self.password.find("°")!=-1) or (self.password.find("¬")!=-1) or (self.password.find("´")!=-1) or (self.password.find("¨")!=-1) or (self.password.find("Ñ")!=-1):
                return "La contraseña debe estar codificada a uft8"
            elif (self.actualName==self.name):
                return None
            elif (accountRegistered):
                return "El nombre de la cuenta debe ser unico"
        return None

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)

class Users_profile(Base):
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    accounts = db.relationship("Users_accounts", backref="user", lazy="dynamic")

class Users_accounts(Base):
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(999))
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.LargeBinary(length=None), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users_profile.id"), nullable=False)

@app.before_request
def before_request():
    if "username" in session:
        g.user=session["username"]
    else:
        g.user=None

@app.route("/")
def index():
    if not g.user:
        return render_template("index.html")
    return redirect(url_for('admin'))

@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method=="POST":
        if  not g.user:
            data=current_account(username=request.form["contactUsername"],email=request.form["contactEmail"],title=request.form["contactTitle"],message=request.form["contactMessage"])
        else:
            user = Users_profile.query.filter_by(username=g.user).first()
            data=current_account(username=user.username,email=user.email,title=request.form["contactTitle"],message=request.form["contactMessage"])
        msg = Message(f"{data.title}-{data.username}", sender= app.config["MAIL_USERNAME"], recipients=[app.config["MAIL_USERNAME"]])
        msg.html = render_template("mail.html", data=data)
        mail.send(msg)
        flash("Mensaje enviado exitosamente", "alert alert-success")
    if g.user:
        return render_template("contact.html")
    return redirect(url_for("login"))

@app.route("/generate")
def generate():
    password=""
    if request.args.get("generateSize"):
        password=generate_password(letters=request.args.get("generateLetters"),numbers=request.args.get("generateNumbers"),symbols=request.args.get("generateSymbols"),size=int(request.args.get("generateSize")))
    return render_template("generate.html", password=password)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if not g.user:
        data=[]
        if request.method=="POST":
            data=current_account(username=request.form["signupUsername"],email=request.form["signupEmail"],password=request.form["signupPassword"],checkPassword=request.form["signupConfirmpassword"])
            signupUser=signup_procedure(data.username,data.email,data.password,data.checkPassword)
            error_message=signupUser.requeriments()
            if error_message:
                flash(error_message,"alert alert-warning")
            else:
                password=generate_password_hash(data.password, method="sha256")
                return redirect(url_for("check", username=data.username,email=data.email,password=password))
        return render_template("signup.html", data=data)
    return redirect(url_for("admin"))

@app.route("/check", methods=["GET","POST"])
def check():
    if not "code" in session:
        if not request.args.get("email") or not request.args.get("password"):
            return redirect(url_for('index'))
        session["code"]=verification_code()
        session["current_username"]=request.args.get("username")
        session["current_email"]=request.args.get("email")
        session["current_password"]=request.args.get("password")
        msg = Message("Sakura Secure Passwords Verificacion de email", sender= app.config["MAIL_USERNAME"], recipients=[session["current_email"]])
        msg.html = render_template("verify.html", code=session["code"])
        mail.send(msg)
        flash("Codigo enviado exitosamente","alert alert-success")
        return redirect(url_for("check"))
    if request.method=="POST":
        if request.form["again"]=="True":
            msg = Message("Sakura Secure Passwords Verificacion de email", sender= app.config["MAIL_USERNAME"], recipients=[session["current_email"]])
            msg.html = render_template("verify.html", code=session["code"])
            mail.send(msg)
            flash("Codigo enviado exitosamente","alert alert-success")
            return redirect(url_for("check"))
        if request.form["checkCode"]==session["code"]:
            new_user=Users_profile(username=session["current_username"], email=session["current_email"],password=session["current_password"])
            db.session.add(new_user)
            db.session.commit()
            email=session["current_email"]
            session.pop("current_username", None)
            session.pop("current_email", None)
            session.pop("current_password", None)
            flash("Te has registrado exitosamente","alert alert-success")
            return redirect(url_for("login",email=email))
        flash("El codigo ingresado es incorrecto", "alert alert-danger")
        return redirect(url_for("check"))
    return render_template("check.html")

@app.route("/login", methods=["GET","POST"])
@app.route("/login/<email>", methods=["GET","POST"])
def login(email=""):
    if not g.user:
        data=current_account(email=email)
        if request.method=="POST":
            data=current_account(email=request.form["loginEmail"],password=request.form["loginPassword"])
            user=Users_profile.query.filter_by(email=data.email).first()
            if user and check_password_hash(user.password, data.password):
                session["username"]=user.username
                flash("Has iniciado sesion correctamente","alert alert-success")
                return redirect(url_for("admin"))
            flash("Tus datos son invalidos","alert alert-danger")
        return render_template("login.html", data=data)
    return redirect(url_for("admin"))

@app.route("/admin", methods=["GET","POST"])
def admin():
    if g.user:
        cipher=AESCipher()
        accounts, account, name, password, passwords, columns, temporalAccount= [], [], None, "",[],"4",[]
        user=Users_profile.query.filter_by(username=g.user).first()
        if request.args.get("temporalName")!=None:
            temporalAccount=current_account(name=request.args.get("temporalName"),username=request.args.get("temporalUsername"),password=request.args.get("temporalPassword"),url=request.args.get("temporalUrl"))
        if user.accounts.all():
            if "columns" in session:
                columns = session["columns"]
            name=request.args.get("name")
            account=user.accounts.filter_by(name=name).first()
            accounts=user.accounts.order_by(Users_accounts.id).all()
            for x in accounts:
                passwords.append(cipher.decrypt(x.password))
            if account:
                password=cipher.decrypt(account.password)
                Data_Write(account,password)
        return render_template("admin.html", accounts=accounts, account=account, password=password, user=user, passwords=passwords, columns=columns, temporalAccount=temporalAccount)
    return redirect(url_for("login"))

@app.route("/account/<name>")
def account(name=None):
    if g.user:
        cipher=AESCipher()
        user=Users_profile.query.filter_by(username=g.user).first()
        if user.accounts.all():
            data=Users_accounts.query.filter_by(user_id=user.id).first()
            accounts=user.accounts.order_by(Users_accounts.id).all()
            account=data.query.filter_by(name=name).first()
            if account:
                password=cipher.decrypt(account.password)
                Data_Write(account,password)
                return render_template("account.html", account=account, accounts=accounts, password=password)
        flash("La cuenta no existe", "alert alert-warning")
        return redirect(url_for("admin"))
    return redirect(url_for("login"))

@app.route("/add", methods=["GET","POST"])
def add():
    if request.method=="POST":
        cipher=AESCipher()
        data=current_account(name=request.form["addName"],url=request.form["addUrl"],username=request.form["addUsername"],password=request.form["addPassword"])
        addAccount=add_procedure(name=data.name,actualName=None,password=data.password)
        error_message=addAccount.requeriments()
        if error_message:
            flash(error_message,"alert alert-warning")
        else:
            data.password=cipher.encrypt(data.password)
            user=Users_profile.query.filter_by(username=g.user).first()
            new_account=Users_accounts(name=data.name, url=data.url, username=data.username,password=data.password, user_id=user.id)
            db.session.add(new_account)
            db.session.commit()
            flash("Cuenta añadida correctamente","alert alert-success")
            return redirect(url_for("admin"))
    return redirect(url_for("admin", temporalName=data.name,temporalUsername=data.username,temporalPassword=data.password,temporalUrl=data.url))

@app.route("/edit/<name>", methods=["GET","POST"])
def edit(name):
    if request.method=="POST":
        user=Users_profile.query.filter_by(username=g.user).first()
        account=user.accounts.filter_by(name=name)
        if not account.first():
            flash("Cuenta no encontrada","alert alert-danger")
            return redirect(url_for('admin'))
        cipher=AESCipher()
        editAccount=add_procedure(name=request.form["editName"],actualName=name,password=request.form["editPassword"])
        error_message=editAccount.requeriments()
        if error_message:
            flash(error_message,"alert alert-warning")
        else:
            data=current_account(name=request.form["editName"],url=request.form["editUrl"],username=request.form["editUsername"],password=request.form["editPassword"])
            password=cipher.encrypt(data.password)
            account.update(dict(name=data.name, url=data.url, username=data.username,password=password, user_id=user.id))
            db.session.commit()
            flash("Cuenta editada exitosamente","alert alert-success")
            return redirect(url_for("account",name=data.name))
        flash("Cuenta no encontrada", "alert alert-danger")
    return redirect(url_for('admin'))

@app.route("/delete/<name>")
def delete(name):
    if g.user:
        user=Users_profile.query.filter_by(username=g.user).first()
        account=user.accounts.filter_by(name=name).first()
        if account:
            db.session.delete(account)
            db.session.commit()
            flash("Cuenta eliminada exitosamente", "alert alert-success")
        else:
            flash("Cuenta no encontrada", "alert alert-danger")
        return redirect(url_for('admin'))
    return redirect(url_for("login"))

@app.route("/search")
def search():
    if g.user:
        user=Users_profile.query.filter_by(username=g.user).first()
        if user.accounts.all():
            if request.args.get("searchAccount"):
                return redirect(url_for("account", name=request.args.get("searchAccount")))
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route("/columns/<int:columns>")
def columns(columns):
    session["columns"]=columns
    return redirect(url_for("admin"))

@app.route("/backup")
def backup():
    if g.user:
        databaseBackup()
        flash("Backup exitoso", "alert alert-success")
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("columns", None)
    session.pop("code", None)
    return redirect(url_for("index"))

@app.errorhandler(404)
def E404(err):
    return render_template('E404.html'), 404

@app.errorhandler(500)
def E500(err):
    return render_template('E500.html'), 500


if __name__==('__main__'):
    db.create_all()
    app.run(port=9001)
    mail.init_app(app)
