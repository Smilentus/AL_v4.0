import random

# Как живут боты:
# Смысл в продолжении рода
# 0) Найти место с энергией
# 1) Накопить энергию
# 2) Родить
# 3) Повторить

class Bot(object):
    def __init__(self, x, y, code):
        # Предел энергии = 1000
        # Смерть <= 0
        # Возможность родить >= 750
        self.energy = 100
        self.energyMax = 1000
        self.energyGain = random.randint(1, 10)
        self.divideEnergy = 750
        self.maxDivisions = 1
        self.energyLvl = y
        self.code = code
        self.mindMove = [0, 0]

        # Мозги
        self.brain = [[0 for i in range(2)] for j in range(2)]

        # Персонализация
        self.color = (0, 255, 0)