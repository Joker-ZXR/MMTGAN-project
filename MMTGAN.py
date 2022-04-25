from numpy import array as nparray
from PySide2.QtWidgets import QGraphicsScene, QMessageBox, QGraphicsPixmapItem, QFileDialog, QApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QImage, QPixmap, QIcon
from PySide2.QtCore import Signal,QObject
from SimpleITK import ReadImage
from threading import  Thread
from SimpleITK import GetArrayFromImage
from torchvision import transforms
from PIL import Image
from time import sleep
from os import path as ospath
from pred import pred
from re import compile

def norm(array):
    arr_max = array.max()
    arr_min = array.min()

    norms = (array - arr_min) / (arr_max - arr_min)
    return norms

# 信号库
class SignalStore(QObject):
    # 定义一种信号
    progress_update = Signal(int)

# 实例化
so = SignalStore()

class Input_SHOW:
    def __init__(self):
        super().__init__()
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        self.ui = QUiLoader().load('ui/GUI.ui')

        # 增加输入文件浏览按钮
        self.ui.Inputdatabtn.clicked.connect(self.handleload)
        self.ui.Fileadata.returnPressed.connect(self.handleinput)
        self.ui.Fileadata.setPlaceholderText('请导入nii.gz/dicom格式的影像文件')
        self.ui.InputEdit.setPlaceholderText('输入模态')

        self.transform = transforms.Resize(256)
    def warning(self, filePath):
        pattern = compile('^[A-Za-z0-9./:_]+$')
        if pattern.fullmatch(filePath) is None:
            QMessageBox.critical(
                self.ui,
                '错误',
                '请选择正确的文件路径')
            mode = True
        elif (ospath.basename(filePath))[-6:] != 'nii.gz' and (ospath.basename(filePath))[-3:] != 'dcm' and (ospath.basename(filePath))[-3:] != 'DCM':
            QMessageBox.critical(
                self.ui,
                '错误',
                '请选择正确的数据格式！')
            mode = True
        elif ospath.exists(filePath) is False:
            QMessageBox.warning(
                self.ui,
                '警告',
                '该路径文件不存在！')
            mode = True
        else:
            mode = False
        return mode

    def readImage(self, path):
        # 读取nii.gz文件
        image = ReadImage(path)
        array = GetArrayFromImage(image)
        if (ospath.basename(path))[-3:] == 'dcm' or (ospath.basename(path))[-3:] == 'DCM':
                array = array[0,:,:]
        self.drawimage(array)
        self.ui.InputImage.setScene(self.scene)
        self.ui.InputEdit.setText('输入模态：T1')
        # self.ui.InputImage.show()

    def drawimage(self, arrays):
        # # 使用graphicsView显示图片
        self.scene = QGraphicsScene()  # 创建画布
        # self.ui.Inputimage.setScene(self.scene)  # 把画布添加到窗口
        # self.ui.Inputimage.show()
        array = (norm(arrays)) * 255
        if len(array.shape) != 2:
            QMessageBox.warning(
                self.ui,
                '警告',
                '输入数据维度有误！')
        else:
            array = Image.fromarray(array)
            array = self.transform(array)
            array = array.convert('RGB')
            array = nparray(array)

            # 方法一：
            frame = QImage(array, array.shape[1], array.shape[0], QImage.Format_RGB888)  # 将像素转换为QImage格式
            self.scene.clear()  # 先清空上次的残留
            pix = QPixmap.fromImage(frame)
            item = QGraphicsPixmapItem(pix)  # 创建像素图元
            self.scene.addItem(item)

            # 方法二：用Qlabel
            # self.ui.label.setPixmap(QPixmap.fromImage(frame))
            # self.ui.label.setScaledContents(True)  # 让图片自适应 label 大小

    def handleload(self):
        filePath, _ = QFileDialog.getOpenFileName(self.ui, "选择你要导入的数据")
        self.ui.Fileadata.setText(filePath)
        if self.warning(filePath):
            self.ui.Fileadata.clear()
        else:
            self.readImage(filePath)
            print('Inputdata_path:', filePath)

    def handleinput(self):
        filePath = self.ui.Fileadata.text()
        if self.warning(filePath):
            self.ui.Fileadata.clear()
        else:
            self.readImage(filePath)
            print('Inputdata_path:', filePath)

class Output_SHOW(Input_SHOW):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        # 连接信号到处理的slot函数
        so.progress_update.connect(self.setProgress)
        self.ui.progressBar.setRange(0, 2)

        self.ui.Inputcktbtn.clicked.connect(self.cktload)
        self.ui.Fileckt.returnPressed.connect(self.cktinput)
        self.ui.Fileckt.setPlaceholderText('请导入.pth格式的训练权重文件')
        self.ui.Generate.clicked.connect(self.pred_result)

        self.ui.Output1.setPlaceholderText('生成模态1')
        # self.ui.Output1.setEnabled(False)   # 设置后禁止更改
        self.ui.Output2.setPlaceholderText('生成模态2')
        self.ui.Output3.setPlaceholderText('生成模态3')
        self.ui.Output4.setPlaceholderText('生成模态4')

        # 统计进行中标记，不能同时做两个统计
        self.ongoing = False

    def pbtn(self):
        def workerThreadFunc():
            self.ongoing = True
            for i in range(1, 5):
                # 发出信息，通知主线程进行进度处理
                sleep(0.5)
                so.progress_update.emit(i)
            self.ongoing = False

        if self.ongoing:
            QMessageBox.warning(
                self.ui,
                '警告', '任务进行中，请等待完成')
            return

        worker = Thread(target=workerThreadFunc)
        worker.start()

    # 处理进度的slot函数
    def setProgress(self, value):
        self.ui.progressBar.setValue(value)

    def warnings(self, cktPath):
        pattern = compile('^[A-Za-z0-9./:_]+$')
        if pattern.fullmatch(cktPath) is None:
            QMessageBox.critical(
                self.ui,
                '错误',
                '请选择正确的文件路径')
            mode = True
        elif (ospath.basename(cktPath))[-3:] != 'pth':
            QMessageBox.critical(
                self.ui,
                '错误',
                '请选择正确的数据格式！')
            mode = True
        elif ospath.exists(cktPath) is False:
            QMessageBox.warning(
                self.ui,
                '警告',
                '该路径文件不存在！')
            mode = True
        else:
            mode = False
        return mode

    def pred_result(self):
        filePath = self.ui.Fileadata.text()
        cktPath = self.ui.Fileckt.text()
        print('Load_data:', filePath)
        print('Load_ckt:', cktPath)
        if filePath == '' or cktPath == '':
            QMessageBox.warning(
                self.ui,
                '警告',
                '请载入相关文件！')
        else:
            self.pbtn()
            result = pred(filePath, cktPath)
        self.drawimage(result[0])
        self.ui.Image1.setScene(self.scene)
        self.ui.Output1.setText('生成模态1：T1c')

        self.drawimage(result[1])
        self.ui.Image2.setScene(self.scene)
        self.ui.Output2.setText('生成模态2：T1DIXONC')

        self.drawimage(result[2])
        self.ui.Image3.setScene(self.scene)
        self.ui.Output3.setText('生成模态3：T2')

        self.drawimage(result[3])
        self.ui.Image4.setScene(self.scene)
        self.ui.Output4.setText('生成模态4：pCT')

    def cktload(self):
        cktPath, _ = QFileDialog.getOpenFileName(self.ui, "选择你要导入的数据")
        self.ui.Fileckt.setText(cktPath)
        if self.warnings(cktPath):
            self.ui.Fileckt.clear()
        else:
            print('Checkpoint_path:', cktPath)

    def cktinput(self):
        cktPath = self.ui.Fileckt.text()
        if self.warnings(cktPath):
            self.ui.Fileckt.clear()
        else:
            print('Checkpoint_path:', cktPath)

if __name__ == '__main__':
    app = QApplication([])
    app.setWindowIcon(QIcon('ui/mri.ico'))
    Input = Input_SHOW()
    output = Output_SHOW(Input.ui)
    output.ui.show()
    app.exec_()

