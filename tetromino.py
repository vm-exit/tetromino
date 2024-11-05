import random, time, pygame, sys
from pygame.locals import *

FPS = 25
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

#HOLD
heldPiece = None 
holdingInUse = False

#FONTS
DISPLAYSURF = None
BASICFONT = None
BIGFONT = None

#MUSIC
MUSIC_FILES = ['resources/tetrisb.mid', 'resources/tetrisc.mid']
VOLUME  = 0.5 #range from 0.0 to 1.0.

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


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT, VOLUME
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT, BIGFONT = (pygame.font.Font('freesansbold.ttf', size) for size in (18, 100))
    pygame.display.set_caption('tetromino')

    dragging = False
    
    while True:
        render_background(DISPLAYSURF)
        render_text(DISPLAYSURF, 'tetromino', 50, (WINDOWWIDTH // 2, 100), color=(255, 204, 0))
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
    # setup variables for the start of the game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)

    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()

    load_music()

    pygame.key.set_repeat(0)  # disable keyrepeat

    while True:  # game loop
        if fallingPiece is None:
            # no piece in play, start new piece at the top
            fallingPiece = nextPiece
            nextPiece = getNewPiece()
            lastFallTime = time.time()  # reset lastFallTime

            if not isValidPosition(board, fallingPiece):
                return  # can't fit a new piece on the board, so game over

        checkForQuit()

        for event in pygame.event.get():  # event handling loop
            if event.type == KEYUP:
                if event.key == K_p:
                    # pausing
                    DISPLAYSURF.fill(BGCOLOR)
                    pygame.mixer.music.pause()
                    showTextScreen('paused') 
                    pygame.mixer.music.unpause()

                    current_time = time.time()
                    lastFallTime = lastMoveDownTime = lastMoveSidewaysTime = current_time
                    #keeping the same time for all variables

                    # lastFallTime = time.time()
                    # lastMoveDownTime = time.time() #ugh. probably could assign time.time to a variable and reduce the amount of look ups
                    # lastMoveSidewaysTime = time.time()

                elif event.key in [K_LEFT, K_RIGHT, K_a, K_d, K_DOWN, K_s]:
                    # quit movement on key release
                    movingLeft = movingRight = movingDown = False

            elif event.type == KEYDOWN:
                time_since_last_move = time.time() - lastMoveSidewaysTime

                if event.key in [K_LEFT, K_a, K_RIGHT, K_d]:
                    direction = -1 if event.key in [K_LEFT, K_a] else 1
                    if isValidPosition(board, fallingPiece, adjX=direction) and time_since_last_move > MOVESIDEWAYSFREQ:
                        fallingPiece['x'] += direction
                        lastMoveSidewaysTime = time.time()

                elif event.key in [K_UP, K_w, K_q]:
                    if event.key == K_UP or event.key == K_w:
                        fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
                    else:  # K_q for counter-clockwise rotation
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - (1 if event.key == K_UP or event.key == K_w else -1)) % len(PIECES[fallingPiece['shape']])

                elif event.key in [K_DOWN, K_s]:
                    if isValidPosition(board, fallingPiece, adjY=1) and time.time() - lastMoveDownTime > MOVEDOWNFREQ:
                        fallingPiece['y'] += 1
                        lastMoveDownTime = time.time()
                # "fastdrop"
                elif event.key == K_SPACE:
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                    fallingPiece['y'] += i - 1

        # let the piece fall if it is time to fall
        if time.time() - lastFallTime > fallFreq:
            if not isValidPosition(board, fallingPiece, adjY=1):
                addToBoard(board, fallingPiece)
                score += removeCompleteLines(board)
                level, fallFreq = calculateLevelAndFallFreq(score)
                fallingPiece = None
            else:
                fallingPiece['y'] += 1
                lastFallTime = time.time()


        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        #render_heldpiece()
        if fallingPiece is not None:
            drawPiece(fallingPiece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def handleKeyEvents(fallingPiece, movingLeft, movingRight, movingDown, board):
    global heldPiece, holdingInUse 

    #dictionary key mapping
    key_actions = {
        K_LEFT: lambda: movePiece(fallingPiece, board, -1, 0),                  # left
        K_a: lambda: movePiece(fallingPiece, board, -1, 0),                     # left (alt key)
        K_RIGHT: lambda: movePiece(fallingPiece, board, 1, 0),                  # right
        K_d: lambda: movePiece(fallingPiece, board, 1, 0),                      # right (alt key)
        K_UP: lambda: rotatePiece(fallingPiece, board, 1),                      # rotate clockwise
        K_w: lambda: rotatePiece(fallingPiece, board, 1),                       # rotate clockwise (alt key)
        K_q: lambda: rotatePiece(fallingPiece, board, -1),                      # rotate counterclockwise
        K_DOWN: lambda: movePiece(fallingPiece, board, 0, 1, movingDown=True),  # down
        K_s: lambda: movePiece(fallingPiece, board, 0, 1, movingDown=True),     # down (alt key)
        K_SPACE: lambda: fastFall(fallingPiece, board)                          # fastfall
        #K_c: lambda: holdPiece(fallingPiece, board)                            # holdpiece
    }

    # event queuing
    for event in pygame.event.get():
        if event.type == KEYUP:
            if event.key in (K_LEFT, K_a):
                movingLeft = False   
            elif event.key in (K_RIGHT, K_d):
                movingRight = False 
            elif event.key in (K_DOWN, K_s):
                movingDown = False   

        elif event.type == KEYDOWN:
            if event.key in key_actions: # check if a key has a dictionary defintion mapped to it
                # do the action for the key and upd move states
                movingLeft, movingRight, movingDown = key_actions[event.key]()

    # return upd'd move states
    return movingLeft, movingRight, movingDown


def movePiece(fallingPiece, board, adjX, adjY, movingDown=False):
    if isValidPosition(board, fallingPiece, adjX=adjX, adjY=adjY):
        fallingPiece['x'] += adjX
        fallingPiece['y'] += adjY
        return (True, False, movingDown) if adjX != 0 else (False, True, movingDown)
    return False, False, movingDown

def rotatePiece(fallingPiece, board, direction):
    fallingPiece['rotation'] = (fallingPiece['rotation'] + direction) % len(PIECES[fallingPiece['shape']])
    if not isValidPosition(board, fallingPiece):
        fallingPiece['rotation'] = (fallingPiece['rotation'] - direction) % len(PIECES[fallingPiece['shape']])

    return False, False, False 

def fastFall(fallingPiece, board):
    moveDown(fallingPiece, board, fastFall=True) #drops the piece straight down on its y axis, just like real tetris
    return False, False, False

#
# note: this does not work.
#
# def holdPiece(fallingPiece):
#     global heldPiece, holdingInUse
#
#     if not holdingInUse:
#         if heldPiece is None:
#             heldPiece = fallingPiece
#             fallingPiece = getNewPiece()  
#         else:
#             heldPiece, fallingPiece = fallingPiece, heldPiece
#       
#         holdingInUse = True 

def moveSideways(fallingPiece, movingLeft, movingRight, board):
    direction = -1 if movingLeft else 1 if movingRight else 0
    if direction and isValidPosition(board, fallingPiece, adjX=direction):
        fallingPiece['x'] += direction

#
# old - new one is just a single conditional
# 
# def moveSideways(fallingPiece, movingLeft, movingRight, board):
#     if movingLeft and isValidPosition(board, fallingPiece, adjX=-1): #checks if the new pos (1 unit left) is valid and decreases x by 1
#         fallingPiece['x'] -= 1
#     elif movingRight and isValidPosition(board, fallingPiece, adjX=1): #checks if the new pos (1 unit right) is valid  and increases x by 1
#         fallingPiece['x'] += 1


def moveDown(fallingPiece, board, fastFall=False):
    if fastFall:
        for i in range(1, BOARDHEIGHT):
            if not isValidPosition(board, fallingPiece, adjY=i):
                break
        fallingPiece['y'] += i - 1
        return False  
    else:
        # Regular fall
        if isValidPosition(board, fallingPiece, adjY=1):
            fallingPiece['y'] += 1
            return True
    return False  

    holdingInUse = False #used in holdPiece.

def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def checkForKeyPress():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    checkForQuit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None

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
# note (jordin) - i'll get the hold piece to work later.
#
# def render_heldpiece():
#  if heldPiece is not None:  
#         holdX, holdY = 10, 10  
#         for x in range(TEMPLATEWIDTH):
#             for y in range(TEMPLATEHEIGHT):
#                 if PIECES[heldPiece['shape']][heldPiece['rotation']][y][x] != BLANK:
#                     pixelX, pixelY = convertToPixelCoords(holdX + x, holdY + y)
#                     pygame.draw.rect(DISPLAYSURF, COLORS[heldPiece['color']], (pixelX + 1, pixelY + 1, BOXSIZE - 1, BOXSIZE - 1))
#                     pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[heldPiece['color']], (pixelX + 1, pixelY + 1, BOXSIZE - 4, BOXSIZE - 4))

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


def showTextScreen(text):
    #centre pos calculation
    centerX, centerY = int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2)
    
    # create shadow and text
    for font, color, offset in [(BIGFONT, TEXTSHADOWCOLOR, (0, 0)),
                                (BIGFONT, TEXTCOLOR, (-3, -3))]:
        titleSurf, titleRect = makeTextObjs(text, font, color)
        titleRect.center = (centerX + offset[0], centerY + offset[1])
        DISPLAYSURF.blit(titleSurf, titleRect)
    
    #text rendering
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (centerX, centerY + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    # waiting for keypress..
    while checkForKeyPress() is None:
        pygame.display.update()
        FPSCLOCK.tick()

#
# old - from boilerplate code, new one precalculates the center pos and combines the shadow and text rendering
#
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
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def calculateLevelAndFallFreq(score):
    level = score // 10 + 1
    fallFreq = 0.27 - level * 0.02
    return level, fallFreq

#
# removed unnecessary parentheses 
#
# def calculateLevelAndFallFreq(score):
#     # Based on the score, return the level the player is on and
#     # how many seconds pass until a falling piece falls one space.
#     level = int(score / 10) + 1
#     fallFreq = 0.27 - (level * 0.02)
#     return level, fallFreq

def getNewPiece():
    shape = random.choice(list(PIECES.keys())) #randomly select a piece
    
    newPiece = {
        'shape': shape,
        'rotation': random.randint(0, len(PIECES[shape]) - 1),  # random rotation
        'x': (BOARDWIDTH - TEMPLATEWIDTH) // 2,  # center 
        'y': -2,  # start above the board
        'color': random.randint(0, len(COLORS) - 1)  # random color
    }
    
    return newPiece

# "improved" centering logic aswell as made readable
#
# def getNewPiece():
#     # return a random new piece in a random rotation and color
#     shape = random.choice(list(PIECES.keys()))
#     newPiece = {'shape': shape,
#                 'rotation': random.randint(0, len(PIECES[shape]) - 1),
#                 'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
#                 'y': -2, # start it above the board (i.e. less than 0)
#                 'color': random.randint(0, len(COLORS)-1)}
#     return newPiece

def addToBoard(board, piece):
    shape = piece['shape']
    rotation = piece['rotation']
    pieceColor = piece['color']
    
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[shape][rotation][y][x] != BLANK:
                board_x = x + piece['x']
                board_y = y + piece['y']
                # ensure the piece is within the boards bounds
                if 0 <= board_x < BOARDWIDTH and 0 <= board_y < BOARDHEIGHT:
                    board[board_x][board_y] = pieceColor

#
#made readable and improved bounds checking
#
# def addToBoard(board, piece):
#     # fill in the board based on piece's location, shape, and rotation
#     for x in range(TEMPLATEWIDTH):
#         for y in range(TEMPLATEHEIGHT):
#             if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
#                 board[x + piece['x']][y + piece['y']] = piece['color']

def getBlankBoard():
    return [[BLANK] * BOARDHEIGHT for _ in range(BOARDWIDTH)]

#
# just simpler
#
# def getBlankBoard():
#     # create and return a new blank board data structure
#     board = []
#     for i in range(BOARDWIDTH):
#         board.append([BLANK] * BOARDHEIGHT)
#     return board


def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


#not even going to touch this. last time i did, the interpreter said i was a war criminal.
def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True

def isCompleteLine(board, y):
    return all(board[x][y] != BLANK for x in range(BOARDWIDTH))

#
# using a generator expression, and all() will check if all values of board[x][y] != blank and will short return which is faster than using return false
#
# def isCompleteLine(board, y):
#     # Return True if the line filled with boxes with no gaps.
#     for x in range(BOARDWIDTH):
#         if board[x][y] == BLANK:
#             return False
#     return True

def removeCompleteLines(board):
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1  

    while y >= 0:
        if isCompleteLine(board, y):
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY - 1]
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            numLinesRemoved += 1
        else:
            y -= 1  
    
    return numLinesRemoved

#
# concise loop and reduces redundant operations
#
# def removeCompleteLines(board):
#     # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
#     numLinesRemoved = 0
#     y = BOARDHEIGHT - 1 # start y at the bottom of the board
#     while y >= 0:
#         if isCompleteLine(board, y):
#             # Remove the line and pull boxes down by one line.
#             for pullDownY in range(y, 0, -1):
#                 for x in range(BOARDWIDTH):
#                     board[x][pullDownY] = board[x][pullDownY-1]
#             # Set very top line to blank.
#             for x in range(BOARDWIDTH):
#                 board[x][0] = BLANK
#             numLinesRemoved += 1
#             # Note on the next iteration of the loop, y is the same.
#             # This is so that if the line that was pulled down is also
#             # complete, it will be removed.
#         else:
#             y -= 1 # move on to check next row up
#     return numLinesRemoved


def convertToPixelCoords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == BLANK:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def drawBoard(board):
    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
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
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


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