from enum import Enum
import random


class Choice(Enum):
    NONE = 0
    ROCK = 1
    PAPER = 2
    SCISSORS = 3


class MatchResult(Enum):
    LOSE = 0
    WIN = 1


class Game:
    def __init__(self, window):
        self.round = 1
        self.updateCount = 0
        self._delay = False

        self.aiHand = Choice.NONE
        self._continue = True
        self._isEnded = False
        self.window = window

    def update(self, playerHand):
        # print(self.updateCount == 201)
        if self._delay:
            self.updateCount += 1
            if self._isEnded:
                if self.updateCount == 70:
                    self.window.winlose.setText(f"{self.round - 2}점")
                if self.updateCount >= 200:
                    self._delay = False
                    self.updateCount = 0
                    self.window.gameEnd()
            else:
                if self.updateCount >= 60:
                    self._delay = False
                    self.updateCount = 0
                    self.window.updateToQ()
            return

        self.window.updateTime()

        if self._continue:
            self.updateCount += 1
            if self.updateCount >= 50:  # CheckHand
                if playerHand == Choice.NONE:
                    self._continue = False
                else:
                    self.window.updateWinLose(self.match(playerHand))
                    self.updateCount = 0
                    self._delay = True
                    self.round += 1

        else:
            if playerHand == Choice.NONE:
                return
            else:
                self._continue = True
                self.window.updateWinLose(self.match(playerHand))
                self.updateCount = 0
                self._delay = True
                self.round += 1

    def match(self, playerHand):
        if self.round <= 3:  # 기본으로 3점 주고 시작하자
            if playerHand == Choice.ROCK:
                self.aiHand = Choice.SCISSORS
            elif playerHand == Choice.PAPER:
                self.aiHand = Choice.ROCK
            else:
                self.aiHand = Choice.PAPER
            self.window.updateAiImage()
            return MatchResult.WIN

        while True:
            self.aiHand = Choice(random.randrange(1, 4))
            if playerHand == self.aiHand:
                continue
            else:
                break
        self.window.updateAiImage()
        if playerHand == Choice.ROCK:
            if self.aiHand == Choice.PAPER:
                return MatchResult.LOSE
            else:
                return MatchResult.WIN
        elif playerHand == Choice.PAPER:
            if self.aiHand == Choice.SCISSORS:
                return MatchResult.LOSE
            else:
                return MatchResult.WIN
        else:  # SCISSOR
            if self.aiHand == Choice.ROCK:
                return MatchResult.LOSE
            else:
                return MatchResult.WIN

    def gameEnd(self):
        self.updateCount = 0
        self._delay = True
        self._isEnded = True
