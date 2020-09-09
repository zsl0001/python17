import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["os"]}
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="text",
      version="0.1",
      description="My GUI application!",
      options={"build_exe": build_exe_options},
      executables=[Executable(r"D:\PycharmProjects\python17\api_preceipt\preceipt_test\main.py", base=base,icon='2.png')])
