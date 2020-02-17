Code for Kick Tic Tac Toe (KTTT)

Kick Tic Tac Toe is a novelty football training program which can run on any python supported harware MCU device that can interface with properietary PCB having interface supporting I2C bus connection to a matrix of IMUs and other supported hardware features of the program. 

The code of the program is structed as below: 

1- IMU handling file is adoption of easily understable work done by MrTijn/Tijndagamer. I want to give credits to him to give a mapping of the registers and reading and writing methods. I have only added functions which are useful for the Kick Tic Tac Toe program. Any suggestions are most welcome on suggestions for coding standards and better way of rearranging the code. The file I am talking about is : mpu6050.py . 
    I started working on this file right from Arduino , Tinsy ( Thanks to  ) for being initial guiding light. The code by MrTijn is very simple to followthrough actually observing the real-time data from IMU MPU6050. Uncomment some of the code you observe the changes in the value of IMU/s when you shoot the ball into the grid. Well part of also depends on what you are observing. This code specially in method detect() , a very crude algorithm is written with not really established reason of why but purely by intuition. It relies on square root method of gauging a cumulative effects of values with additional logic that is based on putting threshold as a benchmark for detection of a football strike on the properitary fabric surface. 
    
2- Second part of the program is to have drills that are complete focus to the footballing aspect of the KTTT program. Each drill is has a serial number with their description in the files like kttt-dr-...py . The explanation of the drills can be found in the description section of the file. Let me try here to put it in tempelate for better reading. 


kttt-dr-2 : #Description: In this drill. Stop watch will run for 1 minute and kttt counts the number of strikes on the grid.

               
