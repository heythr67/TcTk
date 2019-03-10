#www.sarthlakshman.com:me: tic-tac-toe.py


#Description: Tic-Tac-Toe two player game
import pygame
import random
import time
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
        self.lastmoves = []
        self.winner = None

    def print_board(self):
        global colors
        '''Print the current game board'''
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        print ("\nCurrent board:")
        print(colors)
        for j in range(0,9,3):
           for i in range(3):
               if (self.board[j+i]== '-'):
                   print ("%d |" %(j+i))
                   colors = list(colors)
                   colors[j+i] = (0,0,1)
                   colors = tuple(colors) 
               else:
                    print ("%s |" %self.board[j+i])
                    if (self.board[j+i]== 'O'):
                        colors = list(colors) 
                        colors[j+i]= (0,1,0)
                        colors = tuple(colors)
                    else: 
                        colors =list(colors)
                        colors[j+i]=(1,0,0)
                        colors= tuple(colors)  
           print ("\n")
        Cube()
        pygame.display.flip()
        pygame.time.wait(100)

    def get_free_positions(self):
        '''Get the list of available positions'''

        moves = []
        for i,v in enumerate(self.board):
            if v=='-':
                moves.append(i)
        return moves

    def mark(self,marker,pos):
        '''Mark a position with marker X or O'''
        self.board[pos] = marker
        self.lastmoves.append(pos)

    def revert_last_move(self):
        '''Reset the last move'''

        self.board[self.lastmoves.pop()] = '-'
        self.winner = None

    def is_gameover(self):
        '''Test whether game has ended'''

        #win_positions = [(0,1,2), (3,4,5), (6,7,8), (0,3,6),(1,4,7),(2,5,8), (0,4,8), (2,4,6)]
        win_positions = [(0,1,2), (3,4,5), (6,7,8), (0,5,8),(1,4,7),(2,3,6), (0,4,6), (2,4,8)]
        #print("In game over")
        for i,j,k in win_positions:
            if self.board[i] == self.board[j] == self.board[k] and self.board[i] != '-':
                self.winner = self.board[i]
                return True

        if '-' not in self.board:
            self.winner = '-'
            return True

        return False

    def play(self,player1,player2):
        '''Execute the game play with players'''

        self.p1 = player1
        self.p2 = player2
    
        for i in range(9):

            self.print_board()
            
            if i%2==0:
                if self.p1.type == 'H':
                    print ("\t\t[Human's Move]")
                else:
                    print ("\t\t[Computer's Move]")
                time.sleep(5) 
                self.p1.move(self)
            else:
                if self.p2.type == 'H':
                    print ("\t\t[Human's Move]")
                else:
                    print ("\t\t[Computer's Move]")
                time.sleep(5)
                self.p2.move(self)

            if self.is_gameover():
                self.print_board()
                time.sleep(10)
                if self.winner == '-':
                    print ("\nGame over with Draw")
                else:
                    print ("\nWinner : %s" %self.winner)
                return
	        	

class Human:
    '''Class for Human player'''

    def __init__(self,marker):
        self.marker = marker
        self.type = 'H'
    
    def move(self, gameinstance):

        while True:
            m = input("Input position:")

            try:
                m = int(m)
            except:
                m = -1
        
            if m not in gameinstance.get_free_positions():
                print ("Invalid move. Retry")
            else:
                break
    
        gameinstance.mark(self.marker,m)
         
class AI:
    '''Class for Computer Player'''

    def __init__(self, marker):
        self.marker = marker
        self.type = 'C'

        if self.marker == 'X':
            self.opponentmarker = 'O'
        else:
            self.opponentmarker = 'X'

    def move(self,gameinstance):
        move_position,score = self.maximized_move(gameinstance)
        gameinstance.mark(self.marker,move_position)



    def maximized_move(self,gameinstance):
        ''' Find maximized move'''    
        bestscore = None
        bestmove = None

        for m in gameinstance.get_free_positions():
            gameinstance.mark(self.marker,m)
        
            if gameinstance.is_gameover():
                score = self.get_score(gameinstance)
            else:
                move_position,score = self.minimized_move(gameinstance)
        
            gameinstance.revert_last_move()
            
            if bestscore == None or score > bestscore:
                bestscore = score
                bestmove = m

        return bestmove, bestscore

    def minimized_move(self,gameinstance):
        ''' Find the minimized move'''

        bestscore = None
        bestmove = None

        for m in gameinstance.get_free_positions():
            gameinstance.mark(self.opponentmarker,m)
        
            if gameinstance.is_gameover():
                score = self.get_score(gameinstance)
            else:
                move_position,score = self.maximized_move(gameinstance)
        
            gameinstance.revert_last_move()
            
            if bestscore == None or score < bestscore:
                bestscore = score
                bestmove = m

        return bestmove, bestscore

    def get_score(self,gameinstance):
        if gameinstance.is_gameover():
            if gameinstance.winner  == self.marker:
                return 1 # Won

            elif gameinstance.winner == self.opponentmarker:
                return -1 # Opponent won

        return 0 # Draw

        

if __name__ == '__main__':
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.01, 100.0)

    glTranslatef(0.0,0.0, -10)

    for i in range(random.randint(0,100)):
        game=GAME()     
        player1 = AI("X")
        player2 = AI("O")
        game.play( player1, player2)
