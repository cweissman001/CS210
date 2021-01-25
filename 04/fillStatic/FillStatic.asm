// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/FillStatic.asm

// Blackens the screen, i.e. writes "black" in every pixel. 
// Key presses are ignored.
// This is an intermediate step added by Prof. Davis.

// Put your code here.

@8192
D=A
@sum
M=D



@SCREEN
D=A
M=-1

@screenlocal//needs something to increment and track to location
M=D

(LOOP)
@screenlocal
A=M
M=-1
@sum
D=M
@END
@sum
M=M-1
@screenlocal
M=M+1
@LOOP
D;JGT

(END)
@END
0;JMP