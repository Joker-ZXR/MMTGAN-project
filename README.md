# MMTGAN-project

# Multimodal NMR image synthesis system(one-to-many)

# MMTGAN.exe已经封装好的程序

# 文件夹说明
checkpoint文件夹存放的是模型训练权重文件

dataset文件夹存放了nii.gz/dicom格式的数据文件，用于输入

ui文件夹存放exe的图标文件和QT设计的UI界面文件

# 其他文件
MMTGAN.py用于于QT结合来定义功能


# exe文件的封装命令：
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


# 防止报错：在spec文件后面加上：
for d in a.datas:

    if '_C.cp38-win_amd64.pyd' in d[0]:
    
        a.datas.remove(d)
        
        break
