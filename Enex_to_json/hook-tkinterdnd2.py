"""pyinstaller hook file.
You need to use this hook-file if you are packaging a project using tkinterdnd2.
"""

from PyInstaller.utils.hooks import collect_data_files, eval_statement

datas = collect_data_files('tkinterdnd2')