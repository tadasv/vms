#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "bytecode.h"

#define STACK_SIZE 1024

void _push_reg();
void _pop_reg();
void _mov_reg_imm();
void _mov_reg_reg();
void _mov_reg_addr();
void _mov_addr_reg();
void _mov_reg_ref();
void _inc_reg();
void _dec_reg();
void _add_reg_reg();
void _jmp_ref();
void _jz_reg_ref();
void _mul_reg_reg();
void _jnz_reg_ref();
void _halt();
void _dummy_handler();


typedef void (*handler_f)();

handler_f itable[256];

struct {
  uint32_t eip;
  uint32_t esp;
  uint32_t ebp;
  uint32_t esi;
  uint32_t edi;
  uint32_t eax;
  uint32_t ebx;
  uint32_t ecx;
  uint32_t edx;
} registers;

unsigned char stack[STACK_SIZE];
unsigned char halt = 0;

void dump_regs()
{
  printf("EIP: %08X\nESP: %08X EBP: %08X ESI: %08X EDI: %08X\n"
		 "EAX: %08X EBX: %08X ECX: %08X EDX: %08X\n",
		 registers.eip, registers.esp, registers.ebp,
		 registers.esi, registers.edi, registers.eax,
		 registers.ebx, registers.ecx, registers.edx);
}

void dump_stack()
{
  uint32_t *ptr = (uint32_t*)registers.esp;
  int i = 0;
  printf("Current stack:\n");
  while (ptr < &stack[STACK_SIZE]) {
	if (i % 6 == 0)
	  printf("%08X: ", ptr);
	printf("%08X ", *ptr);
	i++;
	if (i % 6 == 0)
	  printf("\n");
	ptr++;
  }
  printf("\n");
}

uint32_t get_reg_data(char reg)
{
  switch (reg) {
	case 0: return registers.eax;
	case 1: return registers.ebx;
	case 2: return registers.ecx;
	case 3: return registers.edx;
	case 4: return registers.esp;
	case 5: return registers.ebp;
	case 6: return registers.esi;
	case 7: return registers.edi;
	case 8: return registers.eip;
	default: return 0;
  }
}


void set_reg_data(char reg, uint32_t data)
{
  switch (reg) {
	case 0: registers.eax = data; break;
	case 1: registers.ebx = data; break;
	case 2: registers.ecx = data; break;
	case 3: registers.edx = data; break;
	case 4: registers.esp = data; break;
	case 5: registers.ebp = data; break;
	case 6: registers.esi = data; break;
	case 7: registers.edi = data; break;
	case 8: registers.eip = data; break;
  }
}

void init_itable()
{
  int i;
  for (i = 0; i < 256; i++)
	itable[i] = &_dummy_handler;

  itable[0x00] = &_push_reg;
  itable[0x01] = &_pop_reg;
  itable[0x02] = &_mov_reg_imm;
  itable[0x03] = &_mov_reg_reg;
  itable[0x04] = &_mov_reg_addr;
  itable[0x05] = &_mov_addr_reg;
  itable[0x06] = &_mov_reg_ref;
  itable[0x07] = &_inc_reg;
  itable[0x08] = &_dec_reg;
  itable[0x09] = &_add_reg_reg;
  itable[0x0A] = &_jmp_ref;
  itable[0x0B] = &_jz_reg_ref;
  itable[0x0C] = &_jnz_reg_ref;
  itable[0x0D] = &_mul_reg_reg;
  itable[0xFF] = &_halt;
}

uint32_t input = 10;
uint32_t output = 0;


int main(int argc, char **argv)
{

  memset(&registers, 0, sizeof(registers));
  init_itable();

  registers.esp = (uint32_t)&stack[STACK_SIZE];
  registers.eip = (uint32_t)&bytecode;

  /* push output address */
  registers.esp -= 4;
  *(uint32_t*)(registers.esp) = &output;

  /* push input address */
  registers.esp -= 4;
  *(uint32_t*)(registers.esp) = &input;

  while (halt == 0) {
	dump_regs();
	dump_stack();
	unsigned char opcode = *(char*)(registers.eip);
	itable[opcode]();
  }

  printf("%d! = %d\n", input, output);

  return 0;
}


void _dummy_handler()
{
  registers.eip++;
}

void _push_reg()
{
  registers.esp -= 4;
  uint32_t *where = (uint32_t*)(registers.esp);
  *where = get_reg_data(*(char*)(registers.eip + 1));
  registers.eip += 2;
}

void _pop_reg()
{
  char reg = *(char*)(registers.eip + 1);
  set_reg_data(reg, *(uint32_t*)(registers.esp));
  registers.esp += 4;
  registers.eip += 2;
}

void _mov_reg_imm()
{
  char reg = *(char*)(registers.eip + 1);
  uint32_t data = *(uint32_t*)(registers.eip + 2);
  set_reg_data(reg, data);
  registers.eip += 6;
}

void _mov_reg_reg()
{
  char reg1 = *(char*)(registers.eip + 1);
  char reg2 = *(char*)(registers.eip + 2);
  set_reg_data(reg1, get_reg_data(reg2));
  registers.eip += 3;
}

void _mov_reg_addr()
{
  char reg1 = *(char*)(registers.eip + 1);
  char reg2 = *(char*)(registers.eip + 2);
  set_reg_data(reg1, *(uint32_t*)get_reg_data(reg2));
  registers.eip += 3;
}

void _mov_addr_reg()
{
  char reg1 = *(char*)(registers.eip + 1);
  char reg2 = *(char*)(registers.eip + 2);
  *(uint32_t*)get_reg_data(reg1) = get_reg_data(reg2);
  registers.eip += 3;
}

void _mov_reg_ref()
{
  char reg = *(char*)(registers.eip + 1);
  uint32_t offset = *(uint32_t*)(registers.eip + 2);
  set_reg_data(reg, registers.eip + offset);
  registers.eip += 6;
}

void _inc_reg()
{
  char reg = *(char*)(registers.eip + 1);
  set_reg_data(reg, get_reg_data(reg) + 1);
  registers.eip += 2;
}

void _dec_reg()
{
  char reg = *(char*)(registers.eip + 1);
  set_reg_data(reg, get_reg_data(reg) - 1);
  registers.eip += 2;
}

void _add_reg_reg()
{
  char reg1 = *(char*)(registers.eip + 1);
  char reg2 = *(char*)(registers.eip + 2);
  set_reg_data(reg1, get_reg_data(reg1) + get_reg_data(reg2));
  registers.eip += 3;
}

void _jmp_ref()
{
  uint32_t offset = *(uint32_t*)(registers.eip + 1);
  registers.eip += offset;
}

void _jz_reg_ref()
{
  char reg = *(char*)(registers.eip + 1);
  if (get_reg_data(reg) == 0) {
	uint32_t offset = *(uint32_t*)(registers.eip + 2);
	registers.eip += offset;
  } else
	registers.eip += 6;
}

void _jnz_reg_ref()
{
  char reg = *(char*)(registers.eip + 1);
  if (get_reg_data(reg) != 0) {
	uint32_t offset = *(uint32_t*)(registers.eip + 2);
	registers.eip += offset;
  } else
	registers.eip += 6;
}

void _mul_reg_reg()
{
  char reg1 = *(char*)(registers.eip + 1);
  char reg2 = *(char*)(registers.eip + 2);
  set_reg_data(reg1, get_reg_data(reg1) * get_reg_data(reg2));
  registers.eip += 3;
}

void _halt()
{
  registers.eip++;
  halt = 1;
}
