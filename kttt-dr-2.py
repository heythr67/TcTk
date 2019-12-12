
#Description: In this drill. Stop watch will run for 1 minute and kttt counts the number of strikes on the grid.  
import pygame
import random
import time
from gpiozero import LED
from mpu6050 import mpu6050
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

verticies = (
    (0,0,0),
    (2,1,0),
    (1,1,0),
    (1,2,0),
    (2,2,0),
    (1,3,0),
    (2,3,0),
    (1,0,0),
    (2,0,0),
    (0,3,0),
    (3,0,0),
    (3,2,0),
    (3,1,0),
    (0,2,0),
    (0,1,0),
    (3,3,0)

    )

colors = (
    (0,0,1),
    (0,0,1),
    (0,0,1),
    (0,0,1),
    (0,0,1),
    (0,0,1),
    (0,0,1),
    (0,0,1),
    (0,0,1)
    )

surfaces = (
    (0,7,2,14),
    (2,7,8,1),
    (1,8,10,12),
    (1,12,11,4),
    (2,1,4,3),
    (2,3,13,14),
    (4,11,15,6),
    (3,4,6,5),
    (3,5,9,13)
    )

edges = (
    (0,14),
    (0,7),
    (7,2),
    (2,14),
    (1,2),
    (1,8),
    (7,8),
    (8,10),
    (10,12),
    (12,1),
    (12,11),
    (11,4),
    (4,1),
    (3,4),
    (3,2),
    (3,13),
    (14,13),
    (11,15),
    (11,4),
    (15,6),
    (6,4),
    (5,6),
    (5,3),
    (5,9),
    (9,13)
    )

def Cube():
    glBegin(GL_QUADS)
    x=0
    for surface in surfaces:
        for vertex in surface:
                glColor3fv(colors[x])
                glVertex3fv(verticies[vertex])
        x+=1
    glEnd()

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()


class GAME:
    def __init__(self):
        '''Initialize parameters - the game board, moves stack and winner'''

        self.board = [ '-' for i in range(0,9) ]
        self.mpu6050 = [] 
        self.mpu6050 = [ mpu6050(0x68, i) for i in range(1,2)]
        
        self.mpu6050[0].offset= self.mpu6050[0].calculate_offset(5,5,5,5) 

    def print_board(self):
        global colors
        '''Print the current game board'''
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        #print ("\nCurrent board:")
        #print(colors)
        for j in range(0,9,3):
           for i in range(3):
               if (self.board[j+i]== '-'):
                   #print ("%d |" %(j+i))
                   colors = list(colors)
                   colors[j+i] = (0,0,1)
                   colors = tuple(colors) 
               else:
                    #print ("%s |" %self.board[j+i])
                    if (self.board[j+i]== 'O'):
                        colors = list(colors) 
                        colors[j+i]= (0,1,0)
                        colors = tuple(colors)
                    else: 
                        colors =list(colors)
                        colors[j+i]=(1,0,0)
                        colors= tuple(colors)  
           #print ("\n")
        Cube()
        pygame.display.flip()
        pygame.time.wait(100)

    def mark(self,marker,pos):
        '''Mark a position with marker X or O'''
        self.board[pos] = marker
        #self.lastmoves.append(pos)

    #ttt-minmax_final: play()
    def start(self,stpwtch):
        '''Execute the game play with players'''
        green = LED(15)
        green.off()
        detect = -1
        self.count = 0
        detect_adjst = 0 
        count_loop = 0  
        self.time_adjst=0 #from print board
        self.strt_time = time.time()
        pygame.mixer.music.load('metronom60.wav')
        pygame.mixer.music.play()
        print("\n strt_time :  %s"%self.strt_time) 
        print("\n curnt_time : %s"%time.time()) 
        while ((time.time()-self.strt_time - self.time_adjst)< stpwtch): #Seconds lapsed 
            detect_adjst= time.time() 
            self.print_board()
            detect= self.mpu6050[0].detect()
            if detect == 1 : 
              green.on() 
              self.count+=1    
              self.mark("O",1)   #"O" for color 1 for position
              pygame.time.wait(1000) 
            else: 
              green.off() 
              self.mark("-",1)
            detect_adjst= time.time()-detect_adjst
            print("detect_adjst: %s" %detect_adjst) 
            #print("count_loop: %s" %count_loop) 
            count_loop+=1 
            #self.time_adjst = detect_adjst


        self.print_board()
        pygame.mixer.music.stop() 
        print ("\n Count : %s" %self.count)

if __name__ == '__main__':
    pygame.mixer.init(44210,-16,1,1024) 
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.01, 100.0)

    glTranslatef(0.0,0.0, -10)

    #game starts here
    game=GAME()     
    game.start(60)     #60 seconds 
