import pygame

import random, time, pygame, sys, threading
from pygame.locals import *

FPS = 25

FPSCLOCK = None
DISPLAYSURF = None
BASICFONT = None
BIGFONT = None
VOLUME  = 0.5 #range from 0.0 to 1.0.
MUSIC_FILES = ['resources/tetrisb.mid', 'resources/tetrisc.mid']

WINDOWWIDTH = 800 
WINDOWHEIGHT = 600 

BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'


MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

def load_music():
    pygame.mixer.music.load(random.choice(MUSIC_FILES))
    pygame.mixer.music.set_volume(VOLUME)
    pygame.mixer.music.play(-1)

def render_text(screen, text, size, position, color=(255, 255, 255)):
    text_surface = pygame.font.Font('freesansbold.ttf', size).render(text, True, color)
    screen.blit(text_surface, text_surface.get_rect(center=position))

def render_slider(screen, volume):
    slider_rect = pygame.Rect(WINDOWWIDTH - 220, WINDOWHEIGHT - 40, 200, 20)
    pygame.draw.rect(screen, (200, 200, 200), slider_rect)
    pygame.draw.rect(screen, (0, 150, 0), (slider_rect.x, slider_rect.y, slider_rect.width * volume, slider_rect.height))
    return slider_rect

#
#    note (jordin) - old method. new one combines calculations for slider_x and _y in the .Rect instantiation... 
#
#    slider_width = 200
#    slider_height = 20
#    slider_x = WINDOWWIDTH - slider_width - 20
#    slider_y = WINDOWHEIGHT - slider_height - 20
#    slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
#    pygame.draw.rect(screen, (200, 200, 200), slider_rect)
#    pygame.draw.rect(screen, (0, 150, 0), (slider_rect.x, slider_rect.y, slider_rect.width * volume, slider_rect.height))
#    return slider_rect

def render_start_button(screen):
    button_rect = pygame.Rect(300, 400, 200, 50)
    pygame.draw.rect(screen, (0, 150, 0), button_rect, border_radius=10)
    render_text(screen, 'Start Game', 30, button_rect.center, color=(255, 255, 255))
    return button_rect

def render_background(screen):
    screen.fill((30, 30, 30))

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT, VOLUME
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT, BIGFONT = (pygame.font.Font('freesansbold.ttf', size) for size in (18, 100))
    pygame.display.set_caption('tetr0mino')

    dragging = False

    while True:
        render_background(DISPLAYSURF)
        render_text(DISPLAYSURF, 'tetr0mino', 50, (WINDOWWIDTH // 2, 100), color=(255, 204, 0))
        slider_rect = render_slider(DISPLAYSURF, VOLUME)
        render_text(DISPLAYSURF, f'Volume: {int(VOLUME * 100)}%', 24, (slider_rect.centerx, slider_rect.top - 30), color=(255, 255, 255))
        button_rect = render_start_button(DISPLAYSURF)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if slider_rect.collidepoint(event.pos):
                    dragging = True
                elif button_rect.collidepoint(event.pos):
                    runGame()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                VOLUME = min(max((event.pos[0] - slider_rect.x) / slider_rect.width, 0), 1) #this could be done in a 2 step process but its more concise this way
                pygame.mixer.music.set_volume(VOLUME)

    FPSCLOCK.tick(30)

def runGame():
    board = getBlankBoard()
    lastMoveDownTime = lastMoveSidewaysTime = lastFallTime = time.time()
    movingLeft = movingRight = False
    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)

    fallingPiece, nextPiece = getNewPiece(), getNewPiece()
    load_music()

    while True:
        if fallingPiece is None:
            fallingPiece, nextPiece = nextPiece, getNewPiece()
            lastFallTime = time.time()
            if not isValidPosition(board, fallingPiece): return

        checkForQuit()
        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == K_p:
                    DISPLAYSURF.fill(BGCOLOR)
                    pygame.mixer.music.pause()
                    showTextScreen('Paused')
                    pygame.mixer.music.unpause()

                if event.key in {K_LEFT, K_a}:
                    movingLeft = False
                elif event.key in {K_RIGHT, K_d}:
                    movingRight = False

            elif event.type == KEYDOWN:
                if event.key in {K_LEFT, K_a} and isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                elif event.key in {K_RIGHT, K_d} and isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                elif event.key in {K_DOWN, K_s}:
                    if isValidPosition(board, fallingPiece, adjY=1):
                        fallingPiece['y'] += 1  # Move down immediately on key press
                    lastMoveDownTime = time.time()  # Reset the last move down time
                elif event.key in {K_UP, K_w, K_q}:
                    rotationChange = 1 if event.key in {K_UP, K_w} else -1
                    fallingPiece['rotation'] = (fallingPiece['rotation'] + rotationChange) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - rotationChange) % len(PIECES[fallingPiece['shape']])

        # Handle sideways movement with timing
        if movingLeft and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
            if isValidPosition(board, fallingPiece, adjX=-1):
                fallingPiece['x'] -= 1
            lastMoveSidewaysTime = time.time()

        if movingRight and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
            if isValidPosition(board, fallingPiece, adjX=1):
                fallingPiece['x'] += 1
            lastMoveSidewaysTime = time.time()

        # Automatic falling logic
        if time.time() - lastFallTime > fallFreq:
            if isValidPosition(board, fallingPiece, adjY=1):
                fallingPiece['y'] += 1
                lastFallTime = time.time()  # Reset last fall time
            else:
                addToBoard(board, fallingPiece)
                score += removeCompleteLines(board)
                level, fallFreq = calculateLevelAndFallFreq(score)
                fallingPiece = None

        # Drawing
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        if fallingPiece: drawPiece(fallingPiece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def checkForKeyPress():
    checkForQuit()
    events = pygame.event.get(KEYUP)
    
    if events:
        return events[0].key
    return None


def showTextScreen(text):
    center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2)
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = center
    DISPLAYSURF.blit(titleSurf, titleRect)

    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (center[0] - 3, center[1] - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (center[0], center[1] + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while checkForKeyPress() is None:
        pygame.display.update()
        FPSCLOCK.tick()


# def showTextScreen(text):
#     # This function displays large text in the
#     # center of the screen until a key is pressed.
#     # Draw the text drop shadow
#     titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
#     titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
#     DISPLAYSURF.blit(titleSurf, titleRect)

#     # Draw the text
#     titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
#     titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
#     DISPLAYSURF.blit(titleSurf, titleRect)

#     # Draw the additional "Press a key to play." text.
#     pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
#     pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
#     DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

#     while checkForKeyPress() == None:
#         pygame.display.update()
#         FPSCLOCK.tick()


def checkForQuit():
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        elif event.type == KEYUP and event.key == K_ESCAPE:
            terminate()
        else:
            pygame.event.post(event)

def calculateLevelAndFallFreq(score):
    level = score // 10 + 1
    fallFreq = 0.27 - level * 0.02
    return level, fallFreq

def getNewPiece():
    shape = random.choice(list(PIECES.keys()))
    rotation = random.randint(0, len(PIECES[shape]) - 1)
    x = (BOARDWIDTH // 2) - (TEMPLATEWIDTH // 2)
    return {'shape': shape, 'rotation': rotation, 'x': x, 'y': -2, 'color': random.randint(0, len(COLORS) - 1)}

def addToBoard(board, piece):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']

def getBlankBoard():
    return [[BLANK] * BOARDHEIGHT for _ in range(BOARDWIDTH)]

def isOnBoard(x, y):
    return 0 <= x < BOARDWIDTH and y < BOARDHEIGHT 

def isValidPosition(board, piece, adjX=0, adjY=0):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            newX = x + piece['x'] + adjX
            newY = y + piece['y'] + adjY
            if not (isOnBoard(newX, newY) and board[newX][newY] == BLANK):
                return False
    return True
#removed isAboveBoard 
#combined the checks into a single conditional

def isCompleteLine(board, y):
    return all(board[x][y] != BLANK for x in range(BOARDWIDTH))
#used all() along with a generator expression for a faster check, removes the need for a loop and early return

def removeCompleteLines(board):
    numLinesRemoved = 0
    for y in range(BOARDHEIGHT - 1, -1, -1):
        if isCompleteLine(board, y):
            numLinesRemoved += 1
            for pullDownY in range(y, 0, -1):
                board[pullDownY] = board[pullDownY - 1][:]
            board[0] = [BLANK] * BOARDWIDTH
    return numLinesRemoved
#replaced while with for
#utilized slicing to copy rows when pulling down to avoid copying the original row

def convertToPixelCoords(boxx, boxy):
    return (XMARGIN + boxx * BOXSIZE, TOPMARGIN + boxy * BOXSIZE)
#cleaned up parentheses

def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    if color == BLANK:
        return
   
    if pixelx is None and pixely is None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy) 

    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))
#original function was alright, used is none instead of == none because it's clearer



def drawBoard(board):
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])

def drawStatus(score, level):
    for i, text in enumerate([f'Score: {score}', f'Level: {level}']):
        surf = BASICFONT.render(text, True, TEXTCOLOR)
        rect = surf.get_rect(topleft=(WINDOWWIDTH - 150, 20 + i * 30))
        DISPLAYSURF.blit(surf, rect)
#used a loop for the score and level text

# def drawStatus(score, level):
#     # draw the score text
#     scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
#     scoreRect = scoreSurf.get_rect()
#     scoreRect.topleft = (WINDOWWIDTH - 150, 20)
#     DISPLAYSURF.blit(scoreSurf, scoreRect)

#     # draw the level text
#     levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
#     levelRect = levelSurf.get_rect()
#     levelRect.topleft = (WINDOWWIDTH - 150, 50)
#     DISPLAYSURF.blit(levelSurf, levelRect)


def drawPiece(piece, pixelx=None, pixely=None):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx is None and pixely is None:
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawBox(x, y, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def drawNextPiece(piece):
    # draw the "next" text
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    # draw the "next" piece
    drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=100)


if __name__ == '__main__':
    main()