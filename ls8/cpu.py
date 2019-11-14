"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000 
RET = 0b00010001
ADD = 0b10100000 


class CPU:
    """Main CPU class."""
    # Last register reserved for stack pointer(sp)
    sp = -1
    # For CALL and RET program counter
    pc_m = 0
    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.reg[self.sp] = 0xF4
        self.halt = False
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret
        self.branchtable[ADD] = self.handle_add
        self.branchtable[HLT] = self.handle_hlt

    def handle_hlt(self, pc):
        self.halt = True

    def handle_ldi(self, pc):
        value = self.ram_read(pc)
        self.ram_write(pc, value)

    def handle_prn(self, pc):
        self.print_reg(pc)

    def handle_mul(self, pc):
        reg_a = self.ram[pc + 1]
        reg_b = self.ram[pc + 2]
        self.alu('MUL', reg_a, reg_b)

    def handle_add(self, pc):
        reg_a = self.ram[pc + 1]
        reg_b = self.ram[pc + 2]
        self.alu('ADD', reg_a, reg_b)
    
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

    def handle_call(self, pc):
        # Push return address to stack
        return_address = pc + 2
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = return_address

        # Set the pc to the value in the register
        reg_num = self.ram[pc + 1]
        self.pc_m = self.reg[reg_num]

    def handle_ret(self, pc):
        # Pop the return address off the stack
        # Store it in the pc
        self.pc_m = self.ram[self.reg[self.sp]]
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
        reg_num = self.ram[address + 1]
        self.reg[reg_num] = value

    def print_reg(self, address):
        """
        Print the register's value
        """
        reg_num = self.ram[address + 1]
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

        pc = 0

        while not self.halt:
            
            # Get the byte of info
            instruction = self.ram[pc]

            # Get the 2 bit of info for the operand amount
            get_operand_num = instruction >> 6

            # If PC mutators, call or ret
            pc_instruction = 0b00010000
            # 1 if it's a pc instruction and 0 if not
            pc_set = (pc_instruction & instruction) >> 4

            # Run program from branchtable
            try:
                self.branchtable[instruction](pc)
            except Exception as e:
                print(f'Error:{e}\n Index: {pc}')

            # If pc_set is 1: Either CALL or RET
            if pc_set:
                pc = self.pc_m
            else:
                # Increment by: Extracted from the instruction
                pc += get_operand_num + 1