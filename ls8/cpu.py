"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


class CPU:
    """Main CPU class."""
    # Last register reserved for stack pointer(sp)
    sp = -1
    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.reg[self.sp] = 0xF4 
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
    
    def handle_ldi(self, pc):
        value = self.ram_read(pc)
        self.ram_write(pc, value)

    def handle_prn(self, pc):
        self.print_reg(pc)

    def handle_mul(self, pc):
        reg_a = self.ram[pc + 1]
        reg_b = self.ram[pc + 2]
        self.alu('MUL', reg_a, reg_b)

    def handle_push(self, pc):
        # Derement value of last register by 1
        self.reg[self.sp] -= 1
        # From instructions, copy register number from RAM
        reg_num = self.ram[pc + 1]
        # Get the register value from Register
        reg_val = self.reg[reg_num]
        # Save the value to Ram
        self.ram[self.reg[self.sp]] = reg_val

    def handle_pop(self, pc):
        # Use current sp to copy the value from RAM
        val = self.ram[self.reg[self.sp]]
        # From instructions, copy register number from RAM
        reg_num = self.ram[pc + 1]
        # Copy value to register
        self.reg[reg_num] = val
        # Increment value of last register by 1
        self.reg[self.sp] += 1

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print('Usage: ls8.py <progam name>')
            sys.ext(1)
        
        progname = sys.argv[1]

        with open(progname) as f:
            for line in f:
                line = line.split('#')[0]
                line = line.strip()

                if line == '':
                    continue

                # Change the string to integer & binary
                value = int(line, 2)

                self.ram[address] = value
                address += 1

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def ram_read(self, address):
        """
        Read From Ram
        Returns: the value from the ram
        """
        value = self.ram[address + 2]
        return value
        
    def ram_write(self, address, value):
        """
        Write to Register
        """
        reg_num = int(self.ram[address + 1])
        self.reg[reg_num] = value

    def print_reg(self, address):
        """
        Print the register's value
        """
        reg_num = int(self.ram[address + 1])
        print(self.reg[reg_num])

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        halt = False
        pc = 0

        while not halt:
            
            # Get the byte of info
            instruction = self.ram[pc]

            # Get the 2 bit of info for the operand amount
            get_operand_num = instruction >> 6

            # If not HLT
            if instruction != HLT:
                self.branchtable[instruction](pc)

            # If HLT
            elif instruction == HLT:
                halt = True

            # If Error
            else:
                print(f'Unknown instruction at index {pc}')
                sys.exit(1)

            # Increment by: Extracted from the instruction
            pc += get_operand_num + 1