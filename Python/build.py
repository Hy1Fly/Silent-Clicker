import PyInstaller.__main__
import os
import shutil

APP_NAME = "Silent-Clicker"
ICON_PATH = "icon.ico" if os.path.exists("icon.ico") else None

params = [
    "silentclicker-gui.py", 
    "--name", APP_NAME,    
    "--onefile",           
    "--windowed",          
    "--add-data", "icon.ico;.",  
    "--icon", ICON_PATH if ICON_PATH else "NONE",  
    "--noconsole",         
    "--clean",             
    "--distpath", "dist"   
]


params += [
    "--hidden-import", "pynput.keyboard._win32",
    "--hidden-import", "pynput.mouse._win32",
    "--hidden-import", "pynput._util.win32"
]


PyInstaller.__main__.run(params)

print(f"\n{APP_NAME} 已成功打包到 dist 目录!")
