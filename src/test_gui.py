from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QImage, QPixmap, QResizeEvent
from PyQt5.QtCore import Qt
import cv2 as cv
import sys
import os
from pathlib import Path
import numpy as np
from state_representation import Point



class RenderMap(QLabel):
    def __init__(self, parent=None)->None:
        super().__init__(parent)
        self.__original_background = cv.imread(Path(r".\src\white_bg.jpg"))
        self.__rendering_canvas = None
        self.__points = []#[Point(0, 0, 'O', 10), Point(0.5, 0.5, 'X', 10, (0,0,255)), Point(1, 1, 'O', 10)]
        self.__height, self.__width, _ = self.__original_background.shape
        self.__width //= 2
        self.__height //= 2
        self.setGeometry(0, 0, self.__width, self.__height)
        self.update_frame()
       
    def __seperate_points(self)->tuple[list[Point]]:
        x_points = []
        o_points = []
        s = 'o'
        for point in self.__points:
            if point.marker.lower() == s:
                o_points.append(point)
            else:
                x_points.append(point)
        return x_points, o_points

    def rerender_image(self)->None:
        h , w, d = self.__rendering_image.shape
        self.__rendering_canvas = QImage(self.__rendering_image.data, w, h, w*d, QImage.Format_BGR888)
        self.__width, self.__height = w, h
        self.setPixmap(QPixmap.fromImage(self.__rendering_canvas))

    
    def resizeEvent(self, event:QResizeEvent)->None:
        size = event.size()
        self.__width = size.width()
        self.__height = size.height()
        self.update_frame()
        event.accept()

        super().resizeEvent(event)

    def draw_points(self, points=None)->None:
        self.__rendering_image = self.__original_background.copy()
        self.__rendering_image = cv.resize(self.__rendering_image, (self.__width, self.__height))
        if points is not None:
            self.__points = points

        for point in self.__points:
            w, h = self.__width-50, self.__height-50

            x = round((point.x*w)+25)
            y = round((point.y*h)+25)
            r = point.radius
            color = point.color
            self.__rendering_image = cv.circle(self.__rendering_image, (x, y), r, color, cv.FILLED)
            self.__rendering_image = cv.putText(self.__rendering_image, point.marker, 
                                                (x-r, y+r//2), 
                                                cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            self.__rendering_image = cv.putText(self.__rendering_image, str(point.id), 
                                                (x-r*3, y-r), 
                                                cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            

    def update_frame(self)->None:
        self.draw_points()
        self.rerender_image()


class MainWindow(QWidget):
    def __init__(self, parent = None)->None:
        super().__init__(parent)
        self.__main__layout = QVBoxLayout(self)
        self.__refresh_button = QPushButton("Refresh")
        self.__calculate_button = QPushButton("Calculate Proximity")
        self.__items_count = QLineEdit()
        self.__items_count.setText("20")
        self.__top_layout = QHBoxLayout()

        self.__refresh_button.setFixedWidth(200)
        self.__calculate_button.setFixedWidth(200)
        self.__items_count.setFixedWidth(200)

        self.__points_render = RenderMap()
        self.__top_layout.addWidget(self.__refresh_button)
        self.__top_layout.addWidget(self.__calculate_button)
        self.__top_layout.addWidget(self.__items_count)

        self.__top_layout.setAlignment(Qt.AlignLeft)
    
        self.__main__layout.addLayout(self.__top_layout)
        self.__main__layout.addWidget(self.__points_render)

        self.__refresh_button.clicked.connect(self.refresh)
        self.__items_count.returnPressed.connect(self.refresh)
        self.setLayout(self.__main__layout)


    def refresh(self)->None:
        txt = self.__items_count.text()
        if not txt.isspace() and len(txt) > 0:
            number = int(txt)
        else:
            number = 20

        self.__points_render.generate_random_points(number)
        self.__points_render.update_frame()


def main():
    app =  QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()



if __name__ == "__main__":
    main()
