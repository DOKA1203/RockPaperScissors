# pyrcc5 name.qrc -o ./name_rc.py
import json
import time

from PyQt5 import QtWidgets, uic
import sys
import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from cvzone.HandTrackingModule import HandDetector

import resources.name_rc
import resources.form_rc
from game import Choice, Game, MatchResult

webcam = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=1)

class NameWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.gameWindow = GameWindow(self)
        self.gameWindow.showFullScreen()
        self.gameWindow.setVisible(False)
        uic.loadUi("./resources/name.ui", self)

        self.userName = None
        self.start_btn.clicked.connect(self.startGame)
        self.showFullScreen()

    def startGame(self):
        self.userName = self.name.text()
        if self.userName == "":
            return

        self.gameWindow.run()
        self.setVisible(False)

    def endGame(self):
        self.gameWindow.isRunning = False
        self.name.setText("")
        self.gameWindow.setVisible(False)

        self.setVisible(True)


class GameWindow(QtWidgets.QMainWindow):
    def __init__(self, nameWindow):
        super().__init__()
        uic.loadUi("./resources/form.ui", self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)  # 30 milliseconds (33.33 fps)
        self.playerHand = Choice.NONE
        self.game = None
        self.nameWindow = nameWindow

        self.isRunning = False

        # self.showFullScreen()
    def run(self):
        self.isRunning = True
        self.setVisible(True)
        self.game = Game(self)

        self.updateToQ()
    def updateFrame(self):
        if not self.isRunning:
            return
        ret, frame = webcam.read()
        frame = cv2.flip(frame, 1)  # 좌우 반전
        hands, frame = detector.findHands(frame)
        fingers = []
        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            if fingers == [0, 0, 0, 0, 0]:
                self.playerHand = Choice.ROCK  # 주먹
            elif fingers == [1, 1, 1, 1, 1]:
                self.playerHand = Choice.PAPER  # 보
            elif fingers == [0, 1, 1, 0, 0]:
                self.playerHand = Choice.SCISSORS  # 가위
            elif fingers == [1, 1, 0, 0, 0]:
                self.playerHand = Choice.SCISSORS  # 가위
            else:
                self.playerHand = Choice.NONE
        else:
            self.playerHand = Choice.NONE
        self.game.update(self.playerHand)
        self.updateScore()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.player_text.setText(f"{self.playerHand.name}: {fingers}")
        self.player_label.setPixmap(QPixmap.fromImage(q_image))

    def updateAiImage(self):
        self.ai_label.setPixmap(QPixmap(f"resources/images/{self.game.aiHand.value}.png"))

    def updateToQ(self):
        self.ai_label.setPixmap(QPixmap(f"resources/images/0.png"))

    def updateTime(self):
        self.winlose.setText(str(5 - (self.game.updateCount // 10)))

    def updateWinLose(self, mr):

        if mr == MatchResult.WIN:
            self.winlose.setPixmap(QPixmap('resources/images/WIN.png'))
        else:
            self.winlose.setPixmap(QPixmap('resources/images/LOSE.png'))
            # play = multiprocessing.Process(target=playsound, args=('resources/music/ge.mp3',))
            # play.start()

            payload = json.dumps({
                "name": self.nameWindow.userName,
                "score": self.game.round - 1
            })
            headers = {
                'Content-Type': 'application/json'
            }
            # response = requests.request("POST", "https://doka.kr/api/rank/", headers=headers, data=payload)

            self.game.gameEnd()

    def updateScore(self):
        self.score.setText(f"라운드 {self.game.round - 1}")

    def gameEnd(self):
        # self.timer.stop()
        self.nameWindow.endGame()


if __name__ == "__main__":
    # play = multiprocessing.Process(target=playsound, args=('resources/music/ge.mp3',))
    # play.start()
    # playsound('resources/music/ge.mp3')

    app = QtWidgets.QApplication(sys.argv)
    window = NameWindow()
    app.exec_()
