class MIPS_machine:
    def __init__(self):
        """
        self.memory = an array of 32 bit integers
        """
        self.memory = [0]*67108864
        self.registers = [0]*32
        self.hi = 0
        self.lo = 0
        self.PC = 0
        self.IR = None

    def _initialize(self):
        """
        Initializes the MIPS machine by reading a binary file and storing it into the machine's memory
        :return: None
        """
        file = open_file()
        memloc = 0
        try:
            word = file.read(4)

            while word:
                self.memory[memloc] = int.from_bytes(word, byteorder='big')
                memloc += 1
                word = file.read(4)
        finally:
            file.close()

        reg1 = int(input("Enter a value for register 1: "))
        reg2 = int(input("Enter a value for register 2: "))
        self.registers[1] = reg1 & 0xffffffff
        self.registers[2] = reg2 & 0xffffffff
        self.registers[31] = 0xfffffffc

    def _execute(self):
        if self.IR & 0xfc0000ff == 0x0000020:       # ADD
            self._add()
        elif self.IR & 0xfc0000ff == 0x0000022:     # SUB
            self._sub()
        elif self.IR & 0xfc0000ff == 0x00000018:    # MULT
            self._mult()
        elif self.IR & 0xfc0000ff == 0x00000019:    # MULTU
            self._multu()
        elif self.IR & 0xfc0000ff == 0x0000001a:    # DIV
            self._div()
        elif self.IR & 0xfc0000ff == 0x0000001b:    # DIVU
            self._divu()
        elif self.IR & 0xfc0000ff == 0x00000010:    # MFHI
            self._mfhi()
        elif self.IR & 0xfc0000ff == 0x00000012:    # MFLO
            self._mflo()
        elif self.IR & 0xfc0000ff == 0x00000014:    # LIS
            self._lis()
        elif self.IR & 0xfc000000 == 0x8c000000:    # LW
            self._lw()
        elif self.IR & 0xfc000000 == 0xac000000:    # SW
            self._sw()
        elif self.IR & 0xfc0000ff == 0x0000002a:    # SLT
            self._slt()
        elif self.IR & 0xfc0000ff == 0x0000002b:    # SLTU
            self._sltu()
        elif self.IR & 0xfc000000 == 0x10000000:    # BEQ
            self._beq()
        elif self.IR & 0xfc000000 == 0x14000000:    # BNE
            self._bne()
        elif self.IR & 0xfc0000ff == 0x00000008:    # JR
            self._jr()
        elif self.IR & 0xfc0000ff == 0x00000009:    # JALR
            self._jalr()
        else:
            raise ValueError('Unrecognized command of the form 0x' + format(self.IR, '08x'))

    def _add(self):
        s, t, d = self._get_registers()
        self.registers[d] = (self.registers[s] + self.registers[t]) % 2**32

    def _sub(self):
        s, t, d = self._get_registers()
        self.registers[d] = (self.registers[s] - self.registers[t]) % 2**32

    def _mult(self):
        s, t, d = self._get_registers()
        # need to interpret as signed int!
        temp = self._signed(self.registers[s]) * self._signed(self.registers[t])
        self.lo = temp & 0xffffffff
        self.hi = (temp >> 32) & 0xffffffff

    def _multu(self):
        s, t, d = self._get_registers()
        temp = self.registers[s] * self.registers[t]
        self.lo = temp & 0xffffffff
        self.hi = (temp >> 32) & 0xffffffff

    def _div(self):
        s, t, d = self._get_registers()
        # need to interpret as signed int!
        self.lo = (self._signed(self.registers[s]) // self._signed(self.registers[t])) & 0xffffffff
        self.hi = (self._signed(self.registers[s]) % self._signed(self.registers[t])) & 0xffffffff

    def _divu(self):
        s, t, d = self._get_registers()
        self.lo = (self.registers[s] // self.registers[t]) & 0xffffffff
        self.hi = (self.registers[s] % self.registers[t]) & 0xffffffff

    def _mfhi(self):
        s, t, d = self._get_registers()
        self.registers[d] = self.hi

    def _mflo(self):
        s, t, d = self._get_registers()
        self.registers[d] = self.lo

    def _lis(self):
        s, t, d = self._get_registers()
        self.registers[d] = self.memory[self.PC//4]
        self.PC += 4

    def _lw(self):
        import sys
        s, t, d = self._get_registers()
        i = self._get_immediate()
        address = self.registers[s] + i
        if address % 4 != 0:
            raise ValueError("Unaligned access at address 0x" + format(address, '08x'))
        if address == 0xffff0004:
            self.registers[t] = sys.stdin.buffer.read()
        else:
            self.registers[t] = self.memory[address//4]

    def _sw(self):
        import sys
        s, t, d = self._get_registers()
        i = self._get_immediate()
        address = self.registers[s] + i
        if address % 4 != 0:
            raise ValueError("Unaligned access at address 0x" + format(address, '08x'))
        if address == 0xffff000c:
            sys.stdout.buffer.write(self.registers[t] & 0xff)
        else:
            self.memory[address // 4] = self.registers[t]

    def _slt(self):
        s, t, d = self._get_registers()
        s_val = self._signed(self.registers[s])
        t_val = self._signed(self.registers[t])
        if s_val < t_val:
            self.registers[d] = 1
        else:
            self.registers[d] = 0

    def _sltu(self):
        s, t, d = self._get_registers()
        if self.registers[s] < self.registers[t]:
            self.registers[d] = 1
        else:
            self.registers[d] = 0

    def _beq(self):
        s, t, d = self._get_registers()
        i = self._get_immediate()
        if self.registers[s] == self.registers[t]:
            self.PC += i*4

    def _bne(self):
        s, t, d = self._get_registers()
        i = self._get_immediate()
        if self.registers[s] != self.registers[t]:
            self.PC += i*4

    def _jr(self):
        s, t, d = self._get_registers()
        if self.registers[s] % 4 != 0:
            raise ValueError("Unaligned jump at address 0x" + format(self.registers[s], '08x'))
        if self.registers[s] == 0xfffffffc:
            # Default $31 value means return
            self._end()
        else:
            self.PC = self.registers[s]

    def _jalr(self):
        s, t, d = self._get_registers()
        if self.registers[s] % 4 != 0:
            raise ValueError("Unaligned jump at address 0x" + format(self.registers[s], '08x'))
        if self.registers[s] == 0xfffffffc:
            # Default $31 value means return
            self._end()
        else:
            self.PC, self.registers[31] = self.registers[s], self.PC

    def _signed(self, signed):
        if signed < 2**31:
            return signed
        else:
            return signed - 2**32

    def _end(self):
        print("MIPS program completed normally.")
        self._print()
        exit()

    def _print(self):
        for i in range(8):
            print("$" + str(i*4).zfill(2) + " = 0x" + format(self.registers[i*4], '08x'), end='   ')
            print("$" + str(i*4+1).zfill(2) + " = 0x" + format(self.registers[i*4+1], '08x'), end='   ')
            print("$" + str(i*4+2).zfill(2) + " = 0x" + format(self.registers[i*4+2], '08x'), end='   ')
            print("$" + str(i*4+3).zfill(2) + " = 0x" + format(self.registers[i*4+3], '08x'))
        print(" pc = 0x" + format(self.PC, '08x'))

    def _get_registers(self):
        """
        From the IR, gets the registers S, T and D
        Returns in the form (S, T, D)
        :return: Tuple(int, int, int)
        """
        s = (self.IR & 0x03E00000) >> 21
        t = (self.IR & 0x001F0000) >> 16
        d = (self.IR & 0x0000F800) >> 11
        return s, t, d

    def _get_immediate(self):
        """
        From the IR, gets the immediate value i
        :return: int
        """
        imm = self.IR & 0x0000ffff
        if imm < 2**15:
            return imm
        return imm - 2**16

    def run(self):
        self._initialize()
        print("Running MIPS program.")
        while True:
            self.registers[0] = 0
            self.IR = self.memory[self.PC//4]
            self.PC += 4
            self._execute()


def open_file():
    file_name = input('Enter filename: ')
    try:
        file = open(file_name, 'rb')
        return file
    except OSError:
        print("Could not open file")
        exit(-1)

print("##### CS-241 MIPS emulator #####")
mips = MIPS_machine()
mips.run()

# TODO: add debugging mode w/ breakpoints and step by step execution

