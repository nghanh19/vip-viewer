from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import numpy as np
from pathlib import Path
from PIL import Image
import cv2

import matplotlib.image as mpimg
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

import matplotlib.pyplot as plt 
from matplotlib.figure import Figure

# Project dependency
from .UI_MainWindow import Ui_MainWindow
#8 bit vertical motion flow
from .include.flows import Vert_Output_BF_L1_960x816 as VBF1
#8 bit horizontal motion flow
from .include.flows import Hori_Output_BF_L1_960x816 as HBF1
#64 bit spare flow
from .include.flows import Full_Vector_Output_ver2_6 as FVO2

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, args, parent=None):
        super(MainWindow, self).__init__(parent)
        self.w1 = None  # No external window yet.
        self.setupUi(self)
        print(args)
        self._initForms()

        # Global variables
        self._g_ImgPre = []
        self._g_ImgCur = []
        self._g_denseLoaded = False
        self._g_spareLoaded = False
    
    def _initForms(self):
        self.figurePreImg = Figure(figsize=(9,3))
        self.canvasPreImg = FigureCanvas(self.figurePreImg)
        NaviToolbarPreImg = NavigationToolbar(self.canvasPreImg, self)
        self.vBoxPreImg.addWidget(self.canvasPreImg)
        self.vBoxPreImg.addWidget(NaviToolbarPreImg)

        self.figureCurImg = Figure(figsize=(9,3))
        self.canvasCurImg = FigureCanvas(self.figureCurImg)
        NaviToolbarCurImg = NavigationToolbar(self.canvasCurImg, self)
        self.vBoxCurImg.addWidget(self.canvasCurImg)
        self.vBoxCurImg.addWidget(NaviToolbarCurImg)

        self.figureDofFlow = Figure(figsize=(9,3))
        self.canvasDofFlow = FigureCanvas(self.figureDofFlow)
        NaviToolbarDofFlow = NavigationToolbar(self.canvasDofFlow, self)
        self.vBoxDofFlow.addWidget(self.canvasDofFlow)
        self.vBoxDofFlow.addWidget(NaviToolbarDofFlow)

        self.figureSpare = Figure(figsize=(9,3))
        self.canvasSpare = FigureCanvas(self.figureSpare)
        NaviToolbarSpare = NavigationToolbar(self.canvasSpare, self)
        self.bBoxSpsFow.addWidget(self.canvasSpare)
        self.bBoxSpsFow.addWidget(NaviToolbarSpare)

        # Menu actions
        self.actionImport_Image.triggered.connect(self._showDialogImgPre)
        self.actionImport_Current_Image.triggered.connect(self._showDialogImgCur)
        self.actionQuit.triggered.connect(self._Exit_window)

        # Push Button Actions
        self.btnDofDisplay.clicked.connect(self._DenseFlowDisplay)
        self.btnSpsDisplay.clicked.connect(self._SparseFlowDisplay)
        self.radioButton_Hori.clicked.connect(self._HorizontalMotionDisplay)
        self.radioButton_Vert.clicked.connect(self._VerticalMotionDisplay)
        self.btnClose.clicked.connect(self._Exit_window)
        self.btnClear.clicked.connect(self._ClearAll)

    def _DenseFlowDisplay(self):
        # set flag dense flow is loaded
        self._g_denseLoaded = True
        # checking if 'Horizontal Motion Display' button is checked
        if self.radioButton_Hori.isChecked():
            self._HorizontalMotionDisplay()
        # if it is not checked
        else:
            self._VerticalMotionDisplay()

    def _showDialogImgPre(self):
        dir = str(Path.cwd())
        fpath = QFileDialog.getOpenFileName(self, "Image Original", dir, str("Image Files (*.jpg)"))
        fname = str(fpath[0]).split("/")[-1]
        if fpath[0]:
            # To read image from disk, we use
            # cv2.imread function, in below method,
            self._g_ImgPre = cv2.imread(fpath[0], cv2.IMREAD_COLOR)

            # Creating GUI window to display an image on screen
            self.ax_img_pre = self.figurePreImg.subplots()
            self.ax_img_pre.imshow(cv2.cvtColor(self._g_ImgPre, cv2.COLOR_BGR2RGB))
            self.canvasPreImg.draw()
            self.statusbar.showMessage(fname + " is opened", 2000)

    def _showDialogImgCur(self):
        dir = str(Path.cwd())
        fpath = QFileDialog.getOpenFileName(self, "Image Original", dir, str("Image Files (*.jpg)"))
        fname = str(fpath[0]).split("/")[-1]
        if fpath[0]:
            # To read image from disk, we use
            # cv2.imread function, in below method,
            img_cur = cv2.imread(fpath[0], cv2.IMREAD_COLOR)

            # Creating GUI window to display an image on screen
            self.ax_img_cur = self.figureCurImg.subplots()
            self.ax_img_cur.imshow(cv2.cvtColor(img_cur, cv2.COLOR_BGR2RGB))
            self.canvasCurImg.draw()
            self.statusbar.showMessage(fname + " is opened", 2000)

    def _HorizontalMotionDisplay(self):
        # Loading pre image in grayscale
        if self._g_ImgPre == []:
            pass
        elif self._g_denseLoaded == False:
            pass
        else:
            # Clean previous image
            self._ClearDofFlow()
            # Loading data
            hori_flow = np.zeros((408,960,3), dtype=np.int8)
            for i in range(408):
                for j in range(960):
                    if(HBF1.hori_output_BF_L1[j + i*960] == 0x0):
                        hori_flow[i,j] =[0, 0, 0]
                    elif((HBF1.hori_output_BF_L1[j + i*960] & 0x200) == 0x200):
                        hori_flow[i,j] =[((HBF1.hori_output_BF_L1[j + i*960] >> 4) & 0x1F)*(255/(29 + ((HBF1.hori_output_BF_L1[j + i*960] & 0xF)/16))), 0, 0]
                    elif((HBF1.hori_output_BF_L1[j + i*960] & 0x200) == 0x0):
                        hori_flow[i,j] =[0, ((HBF1.hori_output_BF_L1[j + i*960] >> 4) & 0x1F)*(255/(29 + ((HBF1.hori_output_BF_L1[j + i*960] & 0xF)/16))), 0]
            # Display on frame
            hori_flow_to_image = Image.fromarray(hori_flow, mode="RGB")
            self.ax_dof_out = self.figureDofFlow.subplots()
            self.ax_dof_out.imshow(hori_flow_to_image)
            self.canvasDofFlow.draw()
            self.statusbar.showMessage("Horizontal motion displaying !", 2000)

    def _VerticalMotionDisplay(self):
        # Loading pre image in grayscale
        if self._g_ImgPre == []:
            pass
        elif self._g_denseLoaded == False:
            pass
        else:
            # Clean previous image
            self._ClearDofFlow()
            # Loading data
            vert_flow = np.zeros((408,960,3), dtype=np.int8)
            for i in range(408):
                for j in range(960):
                    if(VBF1.vert_output_BF_L1[j + i*960] == 0x0):
                        vert_flow[i,j] =[0, 0, 0]
                    elif((VBF1.vert_output_BF_L1[j + i*960] & 0x200) == 0x200):
                        vert_flow[i,j] =[((VBF1.vert_output_BF_L1[j + i*960] >> 4) & 0x1F)*(255/(29 + ((VBF1.vert_output_BF_L1[j + i*960] & 0xF)/16))), 0, 0]
                    elif((VBF1.vert_output_BF_L1[j + i*960] & 0x200) == 0x0):
                        vert_flow[i,j] =[0, ((VBF1.vert_output_BF_L1[j + i*960] >> 4) & 0x1F)*(255/(29 + ((VBF1.vert_output_BF_L1[j + i*960] & 0xF)/16))), 0]
            # Display
            vert_flow_to_image = Image.fromarray(vert_flow, mode="RGB")
            self.ax_dof_out = self.figureDofFlow.subplots()
            self.ax_dof_out.imshow(vert_flow_to_image)
            self.canvasDofFlow.draw()
            self.statusbar.showMessage("Vertical motion displaying !", 2000)

    def _SparseFlowDisplay(self):
        # set flag dense flow is loaded
        self._g_spareLoaded = True
        # Loading pre image in grayscale
        if self._g_ImgPre == []:
            pass
        elif self._g_spareLoaded == True:
            # Clean previous image
            self._ClearSpsFlow()
        # Loading data
        x = [0 for _ in range(len(FVO2.full_output_vector_ver2))]
        for i in range(len(FVO2.full_output_vector_ver2)):
            x[i] = (FVO2.full_output_vector_ver2[i] >> 48) & 0x3FF

        # y = np.zeros(len(FVO2.full_output_vector_ver2), dtype=np.uint16)
        y = [0 for _ in range(len(FVO2.full_output_vector_ver2))]
        for i in range(len(FVO2.full_output_vector_ver2)):
            y[i] = (FVO2.full_output_vector_ver2[i] >> 32) & 0x3FF

        # u = np.zeros(len(FVO2.full_output_vector_ver2), dtype=np.float64)
        u = [0 for _ in range(len(FVO2.full_output_vector_ver2))]
        for i in range(len(FVO2.full_output_vector_ver2)):
            if((FVO2.full_output_vector_ver2[i] >> 28) & 0x1 == 1):
                u[i] = -128 + ((FVO2.full_output_vector_ver2[i] >> 21) & 0x7F) + ((FVO2.full_output_vector_ver2[i] >> 16) & 0x1F)/32 
            elif((FVO2.full_output_vector_ver2[i] >> 28) & 0x1 == 0):
                u[i] = ((FVO2.full_output_vector_ver2[i] >> 21) & 0x7F) + ((FVO2.full_output_vector_ver2[i] >> 16) & 0x1F)/32

        # v = np.zeros(len(FVO2.full_output_vector_ver2), dtype=np.float64)
        v = [0 for _ in range(len(FVO2.full_output_vector_ver2))]
        for i in range(len(FVO2.full_output_vector_ver2)):
            if(((FVO2.full_output_vector_ver2[i] >> 12) & 0x1) == 1):
                v[i] = -128 + ((FVO2.full_output_vector_ver2[i] >> 5) & 0x7F) + ((FVO2.full_output_vector_ver2[i] & 0x1F)/32 )
            elif(((FVO2.full_output_vector_ver2[i] >> 12) & 0x1) == 0):
                v[i] = ((FVO2.full_output_vector_ver2[i] >> 5) & 0x7F) + ((FVO2.full_output_vector_ver2[i] & 0x1F)/32 )

        z = zip(u, v)
        color = [
            "green" if i[0] > 0 else "red" if i[0] < 0 else (0, 0, 0, 0) for i in z
        ]

        self.ax_spare = self.figureSpare.subplots()

        # Loading pre image in grayscale
        if self._g_ImgPre != []:
            crop_img = self._g_ImgPre[250:658, 614:1530]
            gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
            self.ax_spare.imshow(gray, cmap="gray")

        # Loading spare flow
        self.ax_spare.quiver(x, y, u, v, color=color, scale=800)
        # self.ax_spare.set_title("Sparse flow vectors")
        self.canvasSpare.draw()
        self.statusbar.showMessage("Sparse Flow displaying !", 2000)

    # Clean
    def _ClearPreImg(self):
        self.figurePreImg.clear()
        self.canvasPreImg.draw()

    def _ClearCurImg(self):
        self.figureCurImg.clear()
        self.canvasCurImg.draw()

    def _ClearDofFlow(self):
        self.figureDofFlow.clear()
        self.canvasDofFlow.draw()

    def _ClearSpsFlow(self):
        self.figureSpare.clear()
        self.canvasSpare.draw()

    def _ClearAll(self):
        self._ClearPreImg()
        self._ClearCurImg()
        self._ClearDofFlow()
        self._ClearSpsFlow()

        self._g_denseLoaded = False
        self._g_spareLoaded = False

    # Quit
    def _Exit_window(self, event):
        # close = QMessageBox()
        # close.setText("Are You sure?")
        # close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        # close = close.exec()

        # if close == QMessageBox.Yes:
            sys.exit()
        # else:
        #     pass
