start:  pop esi
        pop edi
        mov eax @esi
        mov ebx int(1)
        jz eax end
loop:   mul ebx eax
        dec eax
        jnz eax loop
end:    mov @edi ebx
        halt
