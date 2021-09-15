import pygame
import time
from pygame import Rect
from bot import *

# Создаём окошко
WIDTH = 1100
HEIGHT = 800
FPS = 30

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
          "GRAY": (70, 70, 70)}

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
event = 50
epoch = 0
earthPole = 0
meteors = 0
totalMeteors = 0
viruses = 0
totalViruses = 0
mercy = 0
totalMercy = 0
currentAlive = 0
currentDead = 0
totalAlive = 0
totalDead = 0
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
        if cases[i][j].isAlive:
            if showEnergy:
                d = int((255 / cases[i][j].energyMax) * cases[i][j].energy)
                if d < 0:
                    d = 0
                if d > 255:
                    d = 255
                return (255, d, 0)
            elif showClans:
                if cases[i][j].code == 999:
                    return (0, 0, 0)
                else:
                    c = cases[i][j].code - 1
                    return COLORS_CLANS[c]
            else:
                return cases[i][j].color
        else:
            return COLORS["GRAY"]
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

# ОН НЕ ЗНАЕТ 
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
    virText = font.render(f'Всего вирусов: {totalViruses}', True, (255, 255, 255))
    screen.blit(virText, (810, 160))
    vir2Text = font.render(f'Новые вирусы: {viruses}', True, (255, 255, 255))
    screen.blit(vir2Text, (810, 190))
    mercyText = font.render(f'Всего воскрешений: {totalMercy}', True, (255, 255, 255))
    screen.blit(mercyText, (810, 220))
    mercy2Text = font.render(f'Воскрешений: {mercy}', True, (255, 255, 255))
    screen.blit(mercy2Text, (810, 250))
    aliveText = font.render(f'Всего живых: {totalAlive}', True, (255, 255, 255))
    screen.blit(aliveText, (810, 280))
    alive2Text = font.render(f'Живых: {currentAlive}', True, (255, 255, 255))
    screen.blit(alive2Text, (810, 310))
    deadText = font.render(f'Всего мёртвых: {totalDead}', True, (255, 255, 255))
    screen.blit(deadText, (810, 340))
    dead2Text = font.render(f'Мёртвые: {currentDead}', True, (255, 255, 255))
    screen.blit(dead2Text, (810, 370))


# Проверка на пограничных соседей
def inBounds(x, y):
    if x < 0 or y < 0 or x >= fieldWidth or y >= fieldHeight:
        return False
    else:
        return True


# Запоминание клеток
def FindNearCases(x, y, r):
    nearCases = []
    if cases[x][y] is not None:
        for sx in range(-r, r + 1):
            for sy in range(-r, r + 1):
                if inBounds(x + sx, y + sy) and x != x + sx and y != y + sy:
                    nearCases.append([x + sx, y + sy])
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
                if inBounds(x + sx, y + sy) and x != x + sx and y != y + sy and cases[x + sx][y + sy] is not None and \
                        cases[x + sx][y + sy].isAlive:
                    if cases[x][y].code == cases[x + sx][y + sy].code:
                        nearCases.append([x + sx, y + sy])
    return nearCases


# Поиск близких противников
def FindNearEnemies(x, y, r):
    nearCases = []
    if cases[x][y] is not None:
        for sx in range(-r, r + 1):
            for sy in range(-r, r + 1):
                if inBounds(x + sx, y + sy) and x != x + sx and y != y + sy and cases[x + sx][y + sy] is not None:
                    if cases[x][y].code != cases[x + sx][y + sy].code or not cases[x + sx][y + sy].isAlive:
                        nearCases.append([x + sx, y + sy])
    return nearCases


def CreateCase(x, y, c):
    cases[x][y] = Bot(x, y, c)
    global totalAlive
    totalAlive += 1


# Уничтожаем клетку
def DestroyCase(x, y):
    cases[x][y].isAlive = False
    global totalDead
    totalDead += 1


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


def LifeCase(i, j):
    if not cases[i][j].isAlive:
        return

    global totalDead

    if cases[i][j].energy <= 0:
        cases[i][j].isAlive = False
        totalDead += 1
        return

    if cases[i][j].energy < cases[i][j].energyMax:
        cases[i][j].energy += cases[i][j].energyGain * (cases[i][j].energyLvl + 1)
    if cases[i][j].energy > cases[i][j].energyMax:
        cases[i][j].energy = cases[i][j].energyMax

    rnd = random.randint(0, 3)
    if rnd == 0:
        Move(i, j)
    elif rnd == 1:
        friends = FindNearFriends(i, j, 1)
        for f in friends:
            if cases[i][j].energy >= 50:
                nrg = cases[i][j].energy - 25
                if cases[i][j].energyMax - cases[f[0]][f[1]].energy >= nrg:
                    cases[i][j].energy -= nrg
                    cases[f[0]][f[1]].energy += nrg
                    break
                else:
                    cases[i][j].energy -= cases[i][j].energyMax - cases[f[0]][f[1]].energy
                    cases[f[0]][f[1]].energy = cases[i][j].energyMax
                    break
    elif rnd == 2:
        CreateChild(i, j)
    else:
        enemies = FindNearEnemies(i, j, 1)
        for e in enemies:
            if cases[i][j] is not None and cases[e[0]][e[1]] is not None:
                if cases[e[0]][e[1]].isAlive:
                    if cases[i][j].energy >= cases[e[0]][e[1]].energy:
                        cases[i][j].energy -= cases[e[0]][e[1]].energy
                        DestroyCase(e[0], e[1])
                    else:
                        cases[e[0]][e[1]].energy -= cases[i][j].energy
                        DestroyCase(i, j)
                else:
                    cases[i][j].energy += int(cases[e[0]][e[1]].energy * 0.5)
                    cases[e[0]][e[1]] = None


# На 7 день Бог зациклил жизнь ...
def CycleLife():
    global epoch
    global currentAlive
    global currentDead
    currentDead = 0
    currentAlive = 0
    epoch += 1
    if epoch % event == 0:
        RandomEvent()
    for i in range(0, fieldWidth):
        for j in range(0, fieldHeight):
            if cases[i][j] is not None:
                if cases[i][j].isAlive:
                    currentAlive += 1
                    LifeCase(i, j)
                else:
                    currentDead += 1


# А на 8-й решил порофлить :D
def RandomEvent():
    rnd = random.randint(0, 3)
    global earthPole
    if rnd == 0:
        for i in range(fieldWidth):
            for j in range(fieldHeight):
                if cases[i][j] is not None and cases[i][j].isAlive:
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
                    if inBounds(lnx + i, lny + j) and lnx != lnx + i and lny != lny + j and cases[lnx + i][lny + j] is not None:
                        cases[lnx + i][lny + j].energy -= random.randrange(700, 10000)
    elif rnd == 2:
        global viruses
        global totalViruses
        vir = random.randint(1, 10)
        totalViruses += vir
        viruses = vir
        for i in range(vir):
            sx = random.randint(0, fieldWidth - 1)
            sy = random.randint(0, fieldHeight - 1)
            cases[sx][sy] = Bot(sx, sy, 999)
    elif rnd == 3:
        global mercy
        global totalMercy
        mercy = 0
        count = random.randint(5, 25)
        for c in range(count):
            sx = random.randint(0, fieldWidth - 1)
            sy = random.randint(0, fieldWidth - 1)
            code = random.randint(1, clans + 1)
            for i in range(-5, 6):
                for j in range(-5, 6):
                    if inBounds(sx + i, sy + j) and cases[sx + i][sy + j] is not None and not cases[sx + i][sy + j].isAlive:
                        CreateCase(sx + i, sy + j, code)
                        mercy += 1
                        totalMercy += 1
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