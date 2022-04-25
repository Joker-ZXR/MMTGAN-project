# MMTGAN-project
Multimodal NMR image synthesis system(one-to-many)

MMTGAN.py用于于QT结合来定义功能

封装命令：
pyinstaller -F MMTGAN.py 
            --noconsole 
            --hidden-import PySide2.QtXml  
            --icon "..\ui\mri.ico"  
            --add-data "..\data_crop.py;."  
            --add-data "..\model.py;."  
            --add-data "..\pred.py;."  
            --workpath "..\build"  
            --distpath "..\dist"  
            –-specpath "..\pkg_exe"

防止报错：在spec文件后面加上：
for d in a.datas:
    if '_C.cp38-win_amd64.pyd' in d[0]:
        a.datas.remove(d)
        break
