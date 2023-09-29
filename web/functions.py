import base64,os,shutil
from Crypto import Random
from Crypto.Cipher import AES
from app import url_for, g
from random import choice
from datetime import date


def Data_Write(account, password):
    file_name=url_for('static',filename='Accounts/Selected_Account.txt').replace("/","",1)
    file=open(file_name,'w')
    file.write(f"""name = {account.name}
url = {account.url}
username = {account.username}
password = {password}
account_id = {account.id}
user_id = {account.user_id}""")
    file.close()

def Data_Read(parameter,name):
    return parameter.replace(f"{name} = ","",1).replace("\n","",1)

def verification_code():
    CHAIN="1234567890"
    return "".join( [choice(CHAIN) for i in range(8)] )

def generate_password(letters, numbers, symbols, size):
    chain="""1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!$%&#()=?+*"""
    if not letters=="true":
        chain=chain.replace("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ","")

    if not numbers=="true":
        chain=chain.replace("1234567890","")

    if not symbols=="true":
        chain=chain.replace("!$%&#()=?+*","")

    if not letters=="true" and not numbers=="true" and not symbols=="true":
        chain="01"
    return "".join( [choice(chain) for i in range(size)] )

class current_account():
    def __init__(self, account="", name="", username="", email="", password="", checkPassword="", url="", title="", message="", code=""):
        self.account=account
        self.name=name
        self.username=username
        self.email=email
        self.password=password
        self.checkPassword=checkPassword
        self.url=url
        self.title=title
        self.message=message
        self.code=code


class AESCipher:

    def __init__(self): 
        self.bs = 32
        self.key = os.environ["AES_KEY"]

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

def databaseBackup():
    print(os.path.abspath("database.db"))
    shutil.copy(os.path.abspath("database.db"), f"/home/nicolas/Plantillas/Backups/{date.today()}.db")
