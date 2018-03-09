# CS241-MIPS-Emulator
MIPS machine emulator for the cs241 dialect of MIPS, written in python3

# How to use

## 1 - The assembler
The assembler is simple to use.

    username$ ./asm < {input_filename} > {output_filename}

This assembles your input file of MIPS assembly and outputs a binary machine language representation.

## 2 - The Emulator
First we start the emulator:

    username$ python3 emulator.py

When prompted for debug mode, just enter 'y' or 'n'.
If you are not debugging, you will be prompted the file name and then for two integers to be put into $1 and $2 (just like cs241-twoints). 

Your program will run and if it doesn't crash, it will output all the registers at the end.


![sample program](./readme_images/sample.png?raw=true "Title")


### 2.1 - Breakpoints
If you choose to use debug mode, you will be prompted for a list of breakpoints. The breakpoints make the machine stop running **before** execution of the nth instruction, counting from 0.

For example:

![breakpoints](./readme_images/breakpoints.png?raw=true "Title")



![breakpoints 1](./readme_images/breakpoints_1.png?raw=true "Title")

### 2.2 - Debug commands

When you hit a breakpoint, you can enter the following commands:

n - executes current line and stops before the next line

c - continues executing until hitting another breakpoint

p - print registers, PC and IR