#import needed files, you must have pygame and python 2.7 installed for this game to work
import math, pygame, sys
from pygame.locals import *
import os, sys, inspect
import time, thread
import winsound


# Determine OS before importing Leap. Windows systems have to support both x86 and x64 so the folder structure
# has to be loaded differently from MAC. 
# Leap documentation: https://developer.leapmotion.com/documentation/python/devguide/Project_Setup.html

# nt = Windows machine
if os.name == 'nt':   
    print "Windows OS detected"
    src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    lib_dir= '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
    sys.path.insert(0, os.path.abspath(os.path.join(src_dir, lib_dir)))   
#else machine = linux or mac
else:
    print "MAC/Linux OS detected"
    src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    lib_dir = os.path.abspath(os.path.join(src_dir,'../lib'))    
    sys.path.insert(0, lib_dir)
    
#Once OS is determined and file structure loaded, import Leap
import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

#Create GUI sizes
WINDOW_WIDTH = 1250
WINDOW_HEIGHT = 700
LINE_THICKNESS = 10
PADDLE_SIZE = 150
PADDLE_OFFSET = 60
PADDLE_BUFFER = 15

#Create color variables
GREEN = (34,139,34)
WHITE = (255,255,255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

#Right hand leap motion offset to keep right hand on the right side of the frame
RIGHT_HAND_X_OFFSET = 700.0
RIGHT_HAND_Y_OFFSET = 220.0

HAND_OFFSET = 150.0

#Left hand leap motion offset to keep left hand on the left side of the frame
LEFT_HAND_X_OFFSET = -200.0
LEFT_HAND_Y_OFFSET = 250.0


RIGHT = WINDOW_HEIGHT/HAND_OFFSET * 2
LEFT = -WINDOW_HEIGHT/HAND_OFFSET * 2
UP = -WINDOW_HEIGHT/HAND_OFFSET * 2
DOWN = WINDOW_HEIGHT/HAND_OFFSET * 2

#Utilize pygame and a little math to create pong table
def drawTable():
    DISPLAY_SURF.fill(GREEN)
    pygame.draw.rect(DISPLAY_SURF, WHITE, ((0,0),
                    (WINDOW_WIDTH, WINDOW_HEIGHT)), LINE_THICKNESS*2 )
    pygame.draw.line(DISPLAY_SURF, WHITE, ((WINDOW_WIDTH/2),0),
                    ((WINDOW_WIDTH/2),WINDOW_HEIGHT), (LINE_THICKNESS/4))

#Create paddle boundries and set the color, left hand = red and right hand = blue
def drawPaddle(paddle, color):
    if paddle.bottom > WINDOW_HEIGHT - LINE_THICKNESS:
            paddle.bottom = WINDOW_HEIGHT - LINE_THICKNESS
    elif paddle.top < LINE_THICKNESS:
        paddle.top = LINE_THICKNESS
    elif paddle.right > WINDOW_WIDTH - LINE_THICKNESS:
        paddle.right = WINDOW_WIDTH - (LINE_THICKNESS + PADDLE_BUFFER)
    elif paddle.left < LINE_THICKNESS:
        paddle.left = LINE_THICKNESS + PADDLE_BUFFER
    #Setting color of paddles
    if color == "RED":
        pygame.draw.rect(DISPLAY_SURF, RED, paddle)
    else:
        pygame.draw.rect(DISPLAY_SURF, BLUE, paddle)



def movePaddle(paddle, deltaY, deltaX):   
    paddle.y = WINDOW_HEIGHT/2-math.floor(deltaY)
    paddle.x = WINDOW_HEIGHT/2-math.floor(deltaX)
    if paddle.bottom > WINDOW_HEIGHT - LINE_THICKNESS:
            paddle.bottom = WINDOW_HEIGHT - LINE_THICKNESS
    elif paddle.top < LINE_THICKNESS:
        paddle.top = LINE_THICKNESS
        
#Draw a white ball
def drawBall(ball):
    pygame.draw.rect(DISPLAY_SURF, WHITE, ball)

#
def moveBall(ball, xDir, yDir, speed):
    ball.x += math.floor(speed*xDir)
    ball.y += math.floor(speed*yDir)
    return ball


def checkEdgeCollision(ball, ballDirX, ballDirY):
    #Check top and bottom collisions, if one exists, change the direction using multiplication of -1
    if ball.top <= (LINE_THICKNESS) or ball.bottom >= (WINDOW_HEIGHT - LINE_THICKNESS):
        ballDirY *= (-1)
    #Check top and bottom collisions, if one exists, change the direction using multiplication of -1
    if ball.left <= (LINE_THICKNESS) or ball.right >= (WINDOW_WIDTH - LINE_THICKNESS):
        ballDirX *= (-1)
    return ballDirX, ballDirY


def checkHitBall(ball, paddle1, paddle2, ballDirX):
    if ball.colliderect(paddle1):
        #Hit paddle sound
        winsound.PlaySound(r'C:\Users\Spencer\Desktop\495 - Final\pong-master\lib\Sound Effects\paddle_hit_sound_effect', winsound.SND_FILENAME)
        return -1
    if ball.colliderect(paddle2):
        winsound.PlaySound(r'C:\Users\Spencer\Desktop\495 - Final\pong-master\lib\Sound Effects\paddle_hit_sound_effect', winsound.SND_FILENAME)
        return -1
    return 1

#A point is scored when the ball touches the edge of the frame
def checkPointScored(ball, score1, score2, ballDirX):
    #Player 2 has scored
    if ball.left <= LINE_THICKNESS:
        return 2
    #Player 1 has scored
    elif ball.right >= WINDOW_WIDTH - LINE_THICKNESS:
        return 1
    #No score
    else:
        return 0


def displayScore(score1, score2, speed):
    resultSurface1 = BASIC_FONT.render('Left Hand = %s' %(score1), True, WHITE)
    resultDisplay1 = resultSurface1.get_rect()
    resultDisplay1.topleft = (35, 35)
    DISPLAY_SURF.blit(resultSurface1, resultDisplay1)

    resultSurface2 = BASIC_FONT.render('Right Hand = %s' %(score2), True, WHITE)
    resultDisplay2 = resultSurface2.get_rect()
    resultDisplay2.topleft = (WINDOW_WIDTH - 180, 35)
    DISPLAY_SURF.blit(resultSurface2, resultDisplay2)
    
def displaySpeed(speed):
    resultSurf3 = BASIC_FONT.render('Speed = %s' %(speed), True, WHITE)
    resultRect3 = resultSurf3.get_rect()
    resultRect3.topleft = ((WINDOW_WIDTH/2 + 10), 650)
    DISPLAY_SURF.blit(resultSurf3, resultRect3)    
    
def displayPowerup(score1, count1, score2, count2):
    if(score1 % 2 == 1) and (count1 % 2 == 1):
        resultSurf4 = BASIC_FONT.render('Speed Boost Available!', True, RED)
        resultRect4 = resultSurf4.get_rect()
        resultRect4.topleft = (350, 50)
        DISPLAY_SURF.blit(resultSurf4, resultRect4)
        
    if(score2 % 2 == 1) and (count2 % 2 == 1):
        resultSurf5 = BASIC_FONT.render('Speed Boost Available!', True, BLUE)
        resultRect5 = resultSurf5.get_rect()
        resultRect5.topleft = (WINDOW_WIDTH - 570, 50)
        DISPLAY_SURF.blit(resultSurf5, resultRect5)  


def reset():
    ballx = WINDOW_WIDTH/2 - LINE_THICKNESS/2
    bally = WINDOW_HEIGHT/2 - LINE_THICKNESS/2

def main():
    pygame.init()
    #Create our controller and frame
    controller = Leap.Controller()
    frame = controller.frame()
    
    #Enable gestures
    controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);  

    #while(not frame.is_valid):
        #frame = controller.frame()
    global DISPLAY_SURF
    global BASIC_FONT, BASIC_FONT_SIZE
    BASIC_FONT_SIZE = 30
    BASIC_FONT = pygame.font.SysFont('helvetica', BASIC_FONT_SIZE)
    DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
    pygame.display.set_caption('Pong')

    score1=0
    score2=0

    ballx = WINDOW_WIDTH/2 - LINE_THICKNESS/2
    bally = WINDOW_HEIGHT/2 - LINE_THICKNESS/2

    playerOnePosition = (WINDOW_HEIGHT - PADDLE_SIZE) / 2
    playerTwoPosition = (WINDOW_HEIGHT - PADDLE_SIZE) / 2

    ballDirX = LEFT
    ballDirY = UP
    
    speed = 1
    count1 = 1
    count2 = 1

    playerOnePaddle = pygame.Rect(PADDLE_OFFSET, playerOnePosition,
                                  LINE_THICKNESS, PADDLE_SIZE)
    playerTwoPaddle = pygame.Rect(WINDOW_WIDTH - PADDLE_OFFSET - LINE_THICKNESS,
                                  playerTwoPosition, LINE_THICKNESS,
                                  PADDLE_SIZE)
    ball = pygame.Rect(ballx, bally, LINE_THICKNESS, LINE_THICKNESS)

    drawTable()
    drawPaddle(playerOnePaddle, "BLUE")
    drawPaddle(playerTwoPaddle, "RED")
    drawBall(ball)

    #Main game loop
    while True: 
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        #Draw table, paddles, and ball
        drawTable()
        drawPaddle(playerOnePaddle, "RED")
        drawPaddle(playerTwoPaddle, "BLUE")
        drawBall(ball)

        frame = controller.frame()
        if frame.is_valid:
            displaySpeed(speed)
            #Determine hands, left hand = player 1, right hand = player 2
            for hand in frame.hands:
                handType = "Left hand" if hand.is_left else "Right hand"
                
                if handType == "Left hand":
                    #we are player 1                    
                    for gesture in frame.gestures():
                        if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                            circle = CircleGesture(gesture)                           
                            #Determine clock direction using the angle between the pointable and the circle normal
                            #This was taken right from the Sample.py file located in the SDK
                            if (circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2) and score1 % 2 == 1 and count1 % 2 == 1:
                                print "Left Hand Speed up gesture activated!"                     
                                speed += .5
                                print 'Speed', speed
                                count1 += 1
                    #Update position of hand and apply offsets        
                    position = hand.palm_position
                    deltaX = (position.y-LEFT_HAND_Y_OFFSET) 
                    deltaY = (-position.x-LEFT_HAND_X_OFFSET) 
                    movePaddle(playerOnePaddle, deltaX, deltaY)
                    
                else:
                    #we are player 2                    
                    for gesture in frame.gestures():
                        if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                            circle = CircleGesture(gesture)                                                
                            #Determine clock direction using the angle between the pointable and the circle normal
                            #This was taken right from the Sample.py file located in the SDK                            
                            if (circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2) and score2 == 1 and count2 == 1:
                                print "Right Hand Speed up gesture activated!"                     
                                speed += .5
                                print 'Speed', speed
                                count2 += 1             
                    #Update position of hand and apply offsets             
                    position = hand.palm_position
                    deltaY = (position.y-RIGHT_HAND_Y_OFFSET) 
                    deltaX = (-position.x-RIGHT_HAND_X_OFFSET) 
                    movePaddle(playerTwoPaddle, deltaY, deltaX)


        ball = moveBall(ball, ballDirX, ballDirY, speed)
        ballDirX, ballDirY = checkEdgeCollision(ball, ballDirX, ballDirY)
        ballDirX = ballDirX * checkHitBall(ball, playerOnePaddle, playerTwoPaddle, ballDirX)
        
        #Call checkPointScored and store result into the point variable
        #A point is scored if the ball edge touches the edge of the frame (minus the line thickness)
        point = checkPointScored(ball, score1, score2, ballDirX)   
        #If checkPointScored returns 1, then player 1 has scored
        if point == 1:
            
            #Scoring sound
            winsound.PlaySound(r'C:\Users\Spencer\Desktop\495 - Final\pong-master\lib\Sound Effects\scoring_sound_effect', winsound.SND_FILENAME)
            score1+=1
            speed += 0.005
            ball.x = WINDOW_WIDTH/2 - LINE_THICKNESS/2
            ball.y = WINDOW_HEIGHT/2 - LINE_THICKNESS/2
            
        #If checkPointScored returns 2, then player 2 has scored
        if point == 2:
            
            #Scoring sound 
            winsound.PlaySound(r'C:\Users\Spencer\Desktop\495 - Final\pong-master\lib\Sound Effects\scoring_sound_effect', winsound.SND_FILENAME)
            score2+=1
            speed += 0.005
            ball.x = WINDOW_WIDTH/2 - LINE_THICKNESS/2
            ball.y = WINDOW_HEIGHT/2 - LINE_THICKNESS/2
            
        #Display new scores, powerups, and speed
        displayScore(score1, score2, speed)
        displayPowerup(score1, count1, score2, count2)
        displaySpeed(speed)
        pygame.display.update()

#Main function
if __name__=='__main__':
        
        main()
