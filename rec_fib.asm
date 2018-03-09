;FIB: Recursive Fibonacci
;
;arguments:
;	$2 - n
;
;returns:
;	$3 - f(n)
;
;registers:
;	$1 - 1
;	$4 - f(n-1)
;	$5 - f(n-2)
;	$6 - temp (comparator, load words)
;	$7 - temp (FIB word)

INIT:	lis $1		;
	.word 1		; Load 1
	lis $7		;
	.word FIB	; Load FIB

FIB:	beq $2, $1, ONE ; if n==1, go to base case
	beq $2, $0, ZERO; if n==0, go to base case

	lis $6
	.word 12	; Load 12
	sub $30, $30, $6; Push stack by 3 words
	sw $31, 0($30)	; 1st word in stack is RA
	sw $2, 4($30)	; 2nd word in stack is n

	sub $2, $2, $1	; (n-1)
	jalr $7		; recurse on f(n-1)
	sw $3, 8($30)	; 3rd word in stack is f(n-1)

	sub $2, $2, $1	; (n-2)
	jalr $7		; recurse on f(n-2)
	add $5, $3, $0	; load f(n-2)

	lw $4, 8($30)	; load f(n-1)
	lw $2, 4($30)	; load n
	lw $31, 0($30)	; load RA
	add $30, $30, $6; finished with stack

	add $3, $4, $5	; return f(n-1) + f(n-2)
	jr $31		;

ONE:	add $3, $1, $0	;return 1
	jr $31		;

ZERO:	add $3, $0, $0	;return 0
	jr $31		;

