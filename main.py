import pygame
import time
from pygame import Rect
from bot import *

# Создаём окошко
WIDTH = 1100
HEIGHT = 800
FPS = 10
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.font.init()
pygame.display.set_caption('Да зародится жизнь...')
clock = pygame.time.Clock()

# Цвета ячеек [Вынести в отдельный файл]
COLORS = {"RED": (255, 0, 0),
          "GREEN": (0, 255, 0),
          "BLUE": (0, 0, 255),
          "WHITE": (255, 255, 255),
          "BLACK": (0, 0, 0),
          "GRAY": (77, 77, 77)}

COLORS_NEIGH = [(255, 0, 0),
                (255, 150, 0),
                (255, 255, 0),
                (0, 255, 255),
                (0, 150, 255),
                (0, 0, 255),
                (255, 0, 255),
                (150, 255, 255),
                (0, 255, 0)]

COLORS_ENERGY = [(255, 0, 0),
                 (255, 70, 0),
                 (255, 130, 0),
                 (255, 190, 0),
                 (255, 255, 0),
                 (255, 255, 0),
                 (200, 250, 0),
                 (160, 240, 0),
                 (130, 230, 0),
                 (90, 220, 0),
                 (0, 255, 0)]

COLORS_CLANS = [(255, 0, 0),
                (0, 255, 0),
                (0, 0, 255),
                (255, 255, 0),
                (255, 0, 255),
                (0, 255, 255),
                (100, 100, 100),
                (50, 150, 255),
                (255, 150, 50),
                (123, 123, 123),
                (100, 255, 100)]

# Настройки
caseSize = 8
fieldWidth = 100
fieldHeight = 100
clans = 10
event = 100
epoch = 0
earthPole = 0
meteors = 0
totalMeteors = 0
# Режимы отображения
displayMode = 'Обычный'
showBorder = 0
showNeigh = 0
showEnergy = 0
showClans = 0

# Хранение
# Карта состояний ячеек
cases = [[None for x in range(0, fieldWidth)] for y in range(0, fieldHeight)]
# Карта для отрисовки ячеек
gameFieldUI = [[None for x in range(0, fieldWidth)] for y in range(0, fieldHeight)]

# Заполнение жизни
def InitField():
    for i in range(0, fieldWidth):
        for j in range(0, fieldHeight):
            if random.randint(0, 101) in range(0, 5):
                CreateCase(i, j, random.randint(1, clans + 1))

def SetColor(i, j):
    if cases[i][j] is not None:
        if showEnergy:
            d = int((255 / 1000) * cases[i][j].energy)
            if d < 0:
                d = 0
            if d > 255:
                d = 255
            return (255, d, 0)
        elif showClans:
            c = cases[i][j].code - 1
            return COLORS_CLANS[c]
        else:
            return COLORS["GREEN"]
    else:
        return COLORS["WHITE"]

# Отрисовка поля
def DrawField():
    for i in range(0, fieldWidth):
        for j in range(0, fieldHeight):
            pygame.draw.rect(screen, SetColor(i, j), Rect(caseSize * i, caseSize * j, caseSize, caseSize), showBorder)
    # Отрисовываем статы
    DrawStats()
    # Двойная буферизация
    pygame.display.flip()   

def DrawStats():
    pygame.draw.rect(screen, (69, 69, 69), Rect(800, 0, 300, 800), 0)
    font = pygame.font.SysFont('Arial', 20)
    epochText = font.render(f'Эпоха: {epoch}', True, (255, 255, 255))
    screen.blit(epochText, (810, 10))
    modeText = font.render(f'Режим: {displayMode}', True, (255, 255, 255))
    screen.blit(modeText, (810, 40))
    poleText = font.render(f'Полюс: {earthPole}', True, (255, 255, 255))
    screen.blit(poleText, (810, 70))
    metText = font.render(f'Всего метеоритов: {totalMeteors}', True, (255, 255, 255))
    screen.blit(metText, (810, 100))
    met2Text = font.render(f'Новые метеориты: {meteors}', True, (255, 255, 255))
    screen.blit(met2Text, (810, 130))


# Проверка на пограничных соседей
def inBounds(x, y):
    if x < 0 or y < 0 or x >= fieldWidth or y >= fieldHeight:
        return False
    else:
        return True

# Запоминание клеток
def FindNearCases(x, y, r):
    nearCases = []
    counter = 0
    if cases[x][y] is not None:
        for sx in range(-r, r + 1):
            for sy in range(-r, r + 1):
                if inBounds(x + sx, y + sy) and x != x + sx and y != y + sy:
                    nearCases.append([x + sx, y + sy])
                if inBounds(x + sx, y + sy) and x != x + sx and y != y + sy and cases[x + sx][y + sy] is not None:
                    counter += 1
    return nearCases

# Поиск пустых клеток рядом
def FindNearEmpty(x, y, r):
    nearCases = []
    if cases[x][y] is not None:
        for sx in range(-r, r + 1):
            for sy in range(-r, r + 1):
                if inBounds(x + sx, y + sy) and x != x + sx and y != y + sy and cases[x + sx][y + sy] is None:
                    nearCases.append([x + sx, y + sy])
    return nearCases

# Поиск близких друзей
def FindNearFriends(x, y, r):
    nearCases = []
    if cases[x][y] is not None:
        for sx in range(-r, r + 1):
            for sy in range(-r, r + 1):
                if inBounds(x + sx, y + sy) and x != x + sx and y != y + sy and cases[x + sx][y + sy] is not None:
                    if  cases[x][y].code == cases[x + sx][y + sy].code:
                        nearCases.append([x + sx, y + sy])
    return nearCases

# Поиск близких противников
def FindNearEnemies(x, y, r):
    nearCases = []
    if cases[x][y] is not None:
        for sx in range(-r, r + 1):
            for sy in range(-r, r + 1):
                if inBounds(x + sx, y + sy) and x != x + sx and y != y + sy and cases[x + sx][y + sy] is not None:
                    if  cases[x][y].code != cases[x + sx][y + sy].code:
                        nearCases.append([x + sx, y + sy])
    return nearCases

def CreateCase(x, y, c):
    cases[x][y] = Bot(x, y, c)

# Уничтожаем клетку
def DestroyCase(x, y):
    cases[x][y] = None

def CreateChild(i, j):
    empty = FindNearEmpty(i, j, 1)
    if len(empty) > 1:
        for d in range(cases[i][j].maxDivisions):
            if cases[i][j].energy >= cases[i][j].divideEnergy:
                cases[i][j].energy -= cases[i][j].divideEnergy
                pos = empty[random.randrange(0, len(empty), 1)]
                CreateCase(pos[0], pos[1], cases[i][j].code)
            else:
                break

def AnalysisMovement(i, j):
    moveCases = FindNearEmpty(i, j, 1)
    if len(moveCases) >= 1:
        rnd = random.randint(0, (len(moveCases) - 1))
        moveDir = moveCases[rnd]
    else:
        moveDir = (i, j)
    return (moveDir[0], moveDir[1])

def Move(i, j):
    dir = AnalysisMovement(i, j)
    if dir[0] != i and dir[1] != j:
        cases[dir[0]][dir[1]] = cases[i][j]
        cases[i][j] = None

def WatchAround():
    pass

def LifeCase(i, j):
    if cases[i][j].energy < 1000:
        cases[i][j].energy += cases[i][j].energyGain * (cases[i][j].energyLvl + 1)
    if cases[i][j].energy > 1000:
        cases[i][j].energy = 1000

    rnd = random.randint(0, 3)
    if rnd == 0:
        Move(i, j)
    elif rnd == 1:
        friends = FindNearFriends(i, j, 1)
        for f in friends:
            if cases[i][j].energy > cases[f[0]][f[1]].energy:
                nrg = cases[i][j].energy
                if 1000 - cases[f[0]][f[1]].energy >= nrg:
                    cases[i][j].energy -= nrg
                    cases[f[0]][f[1]].energy += nrg
                    break
                else:
                    cases[i][j].energy -= 1000 - cases[f[0]][f[1]].energy
                    cases[f[0]][f[1]].energy = 1000
                    break
    elif rnd == 2:
        CreateChild(i, j)
    else:
        enemies = FindNearEnemies(i, j, 1)
        for e in enemies:
            if cases[i][j] is not None and cases[e[0]][e[1]] is not None:
                if cases[i][j].energy >= cases[e[0]][e[1]].energy:
                    cases[i][j].energy -= cases[e[0]][e[1]].energy
                    DestroyCase(e[0], e[1])
                else:
                    cases[e[0]][e[1]].energy -= cases[i][j].energy
                    DestroyCase(i, j)

# На 7 день Бог зациклил жизнь ...
def CycleLife():
    global epoch
    epoch += 1
    if epoch % event == 0:
        RandomEvent()
    for i in range(0, fieldWidth):
        for j in range(0, fieldHeight):
            if cases[i][j] is not None:
                LifeCase(i, j)

# А на 8-й решил порофлить :D
def RandomEvent():
    rnd = random.randint(0, 1)
    global earthPole
    if rnd == 0:
        for i in range(fieldWidth):
            for j in range(fieldHeight):
                if cases[i][j] is not None:
                    if earthPole == 0:
                        cases[i][j].energyLvl = j
                    else:
                        cases[i][j].energyLvl = i
        earthPole += 1
        if earthPole > 1:
            earthPole = 0
    elif rnd == 1:
        global meteors
        global totalMeteors
        meteors = random.randint(5, 50)
        totalMeteors += meteors
        size = random.randint(5, 25)
        for i in range(meteors):
            lnx = random.randint(0, fieldWidth - 1)
            lny = random.randint(0, fieldHeight - 1)
            for i in range(-size, size + 1):
                for j in range(-size, size + 1):
                    if inBounds(lnx + i, lny + j) and lnx != lnx + i and lny != lny + j:
                        cases[lnx + i][lny + j] = None
    elif rnd == 2:
        pass
    else:
        pass

def StartGame():
    InitField()

    global showNeigh
    global showEnergy
    global showClans
    global displayMode

    isRunning = True
    while isRunning:
        # Базовые настройки
        clock.tick(FPS)
        # События
        for event in pygame.event.get():
            # Обработка выхода из игры
            if event.type == pygame.QUIT:
                isRunning = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    showNeigh = 1
                    showEnergy = 0
                    showClans = 0
                    displayMode = 'Обычный'
                if event.key == pygame.K_2:
                    showNeigh = 0
                    showEnergy = 1
                    showClans = 0
                    displayMode = 'Энергия'
                if event.key == pygame.K_3:
                    showNeigh = 0
                    showEnergy = 0
                    showClans = 1
                    displayMode = 'Кланы'

        # Обновление
        CycleLife()
        # Визуализация
        DrawField()
    pygame.quit()
    

if __name__ == '__main__':
    StartGame()