// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

// Put your code here.
//one big loop--two smaller loop with the loops--one for white and one for black 

(DARK)//big loop to keep going and accepting input no matter 
@SCREEN //setting screenlocal val to SCREEN
D=A
@screenlocal
M=D

@KBD //taking the key press
D=M
@BLANK
D;JEQ //white
D=-1 //black


(BLANK)
@color //turning screen dark variable
M=D

(DARKLOOP)
@screenlocal//needs something to increment and track to local
D=M

@KBD
D=D-A
@DARK
D;JGE

@color
D=M

@screenlocal
A=M
M=D

D=A+1 //incrementing screenlocal
@screenlocal
M=D


@DARKLOOP
0;JMP //end of the infinite loop

