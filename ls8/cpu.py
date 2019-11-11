"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, address):
        """
        Read From Ram
        Returns: the value from the ram
        """
        reg_num = int(self.ram[address + 1])
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
        reg_num = int(self.ram[address+1])
        print(self.reg[reg_num])

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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
        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001

        halt = False
        pc = 0

        while not halt:
            instruction = self.ram[pc]

            if instruction == LDI:
                value = self.ram_read(pc)
                self.ram_write(pc, value)
                pc += 3
            elif instruction == PRN:
                self.print_reg(pc)
                pc += 2
            elif instruction == HLT:
                halt = True
                pc += 1
            else:
                print(f'Unknown instruction at index {pc}')
                sys.exit(1)