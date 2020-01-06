
#Description: In this drill. Stop watch will run for 1 minute and kttt counts the number of strikes on the grid.  
import pygame
import random
import time
import os 
import errno
from gpiozero import LED
from mpu6050 import mpu6050
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

#Pygame Cube with assignment of blue background, defining edges , vertices
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
#To enable debug
debug=0
#To create dump of ax, ay, az, gx, gy,gz ,delta_T
record_game = 1
#Device ID
device_id = 'go_pree'
#Subscribed user ID
player_id = 'X'

#All logs to be stored in record_game folder
log_path = os.getcwd()

#Creating cube with openGL library
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


#Defines a game
class GAME:
    #initialize game with no detection on board, 
    def __init__(self):
        '''Initialize parameters - the game board, moves stack and winner'''

        self.board = [ '-' for i in range(0,9) ]
        self.mpu6050 = [] 
        #Calling mpu6050 class to create grid objects (1 grid = 1 sensor)
        self.mpu6050 = [ mpu6050(0x68, i) for i in range(1,2)]
        '''
        Caliberating grid with threshold. A threshold decides how grid detects
        the strike of the ball.
        '''
        self.mpu6050[0].offset= self.mpu6050[0].calculate_offset(5,5,5,5) 


        #recording could be disabled to save space. Just do record_game = 0
        if (record_game):
             try:
                 os.mkdir(log_path+'/record_game')
             except OSError as e:
                 if e.errno == errno.EEXIST: 
                      print('Folder exists')
                 else:
                      raise  
             file_create_time = time.gmtime()
             #Every record is differentiated by the time of creation.
             self.record = open(device_id + '_' + player_id+ '_'+str(file_create_time.tm_year)+str(file_create_time.tm_mon)+str(file_create_time.tm_mday)+str(file_create_time.tm_hour)+str(file_create_time.tm_min)+str(file_create_time.tm_sec)+'.txt','w')
             print('recording game....')    

 
    def print_board(self):
        global colors
        '''Print the current game board'''
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        if (debug): 
              print ("\nCurrent board:")
              print(colors)

        for j in range(0,9,3):
           for i in range(3):
               if (self.board[j+i]== '-'):
                   if (debug):
                       print ("%d |" %(j+i))
                   colors = list(colors)
                   colors[j+i] = (0,0,1)
                   colors = tuple(colors) 
               else:
                    if(debug):
                       print ("%s |" %self.board[j+i])
                    if (self.board[j+i]== 'O'):
                        colors = list(colors) 
                        colors[j+i]= (0,1,0)
                        colors = tuple(colors)
                    else: 
                        colors =list(colors)
                        colors[j+i]=(1,0,0)
                        colors= tuple(colors)  
           if (debug):
                print ("\n")
        Cube()
        #updates the display with current values for the grid.
        pygame.display.flip()
        #This time to let update stay on the display for a while.Change it to see
        #how long green blob stays.
        pygame.time.wait(100)

    def mark(self,marker,pos):
        '''Mark a position with marker X or O'''
        self.board[pos] = marker
        #self.lastmoves.append(pos)

    #ttt-minmax_final: play()
    def start(self,stpwtch):
        '''Execute the game play with players'''
        #Signal to scratch
        green = LED(15)
        #gpio 15 is connected with gpio 14 using a wire.
        green.off()
        detect = []
        #Self.count is added in this drill to count number of strikes.
        self.count = 0
        detect_adjst = 0 
        #count_loop = 0  
        self.time_adjst=0 #from print board
        #loading the background music file
        pygame.mixer.music.load('metronom60.wav')
        self.strt_time = time.time()
        delta_T = self.strt_time
        #Starting the game at Epoch of sound
        pygame.mixer.music.play()
        if (debug):
            print("\n strt_time :  %s"%self.strt_time) 
            print("\n curnt_time : %s"%time.time()) 
        while ((time.time()-self.strt_time - self.time_adjst)< stpwtch): #Seconds lapsed 
            detect_adjst= time.time() 
            self.print_board()
            detect= self.mpu6050[0].detect()
            if (debug):
                print(detect)  
            if detect[0] == 1 : 
              green.on() 
              self.count+=1    
              self.mark("O",1)   #"O" for color 1 for position
              
              delta_T = time.time() -delta_T
              #dumping ax ay az gx gy gz delta_T
              self.record.write(str(detect[1])+' '+str(detect[2])+' '+str(detect[3])+' '+str(detect[4])+' '+str(detect[5])+' '+str(detect[6])+' '+str(delta_T)+'\n')
              delta_T = time.time() 
              pygame.time.wait(1000)
            else: 
              green.off() 
              self.mark("-",1)
            detect_adjst= time.time()-detect_adjst
            if (debug):
                print("detect_adjst: %s" %detect_adjst) 
                print("count_loop: %s" %count_loop) 
                count_loop+=1 
            #Time lost in executing detect() and record.write() gets detected from the game time
            self.time_adjst = detect_adjst


        self.print_board()
        pygame.mixer.music.stop()
        #Tells the number of strikes at the end of the game
        print ("\n Count : %s" %self.count)
        #Saving the log file for the sensors data upon detection
        self.record.close()
 
if __name__ == '__main__':
    pygame.mixer.init(44210,-16,1,1024) 
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.01, 100.0)

    glTranslatef(0.0,0.0, -10)

    #game starts here
    game=GAME()
    #Duration of time : min x 60(sec)
    game.start(60)     # 1 min
