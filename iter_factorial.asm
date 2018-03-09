;n is stored in $1
;n! should be stored in $3
lis $3		;initialize $3
.word 1
add $4, $3, $0  ;set $4 as 1
LOOP:
beq $1, $0, END ;if n is 0, return
mult $1, $3	;prod = prod*n
mflo $3		;
sub $1, $1, $4	;n = n-1
beq $0, $0, LOOP;
END:
jr $31