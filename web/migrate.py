import shutil, os
from datetime import date
from datetime import datetime

print(os.path.abspath("archivo.txt"))
shutil.copy(os.path.abspath("archivo.txt"), f"/home/nicolas/Escritorio/Varios/Scripts/Backups/{date.today()}.db")