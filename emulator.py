class MIPS_machine:
    def __init__(self):
        self._debug_mode = False
        self._breakpoints = set()
        self._break = False
        self._memory = [0] * 67108864
        self._registers = [0] * 32
        self._hi = 0
        self._lo = 0
        self._PC = 0
        self._IR = 0

    def _initialize(self):
        """
        Initializes the MIPS machine by reading a binary file and storing it into the machine's memory
        :return: None
        """
        self._debug_mode = get_debug_mode()
        if self._debug_mode:
            self._breakpoints = get_breakpoints()

        file = open_file()
        memloc = 0
        try:
            word = file.read(4)

            while word:
                self._memory[memloc] = int.from_bytes(word, byteorder='big')
                memloc += 1
                word = file.read(4)
        finally:
            file.close()

        reg1 = int(input("Enter a value for register 1: "))
        reg2 = int(input("Enter a value for register 2: "))
        self._registers[1] = reg1 & 0xffffffff
        self._registers[2] = reg2 & 0xffffffff
        self._registers[30] = 0x10000000
        self._registers[31] = 0xfffffffc

    def _execute(self):
        # read instruction by bit masking the identifying bits
        if self._IR & 0xfc0000ff == 0x0000020:       # ADD
            self._add()
            # print('add')
        elif self._IR & 0xfc0000ff == 0x0000022:     # SUB
            self._sub()
            # print('sub')
        elif self._IR & 0xfc0000ff == 0x00000018:    # MULT
            self._mult()
            # print('mult')
        elif self._IR & 0xfc0000ff == 0x00000019:    # MULTU
            self._multu()
            # print('multu')
        elif self._IR & 0xfc0000ff == 0x0000001a:    # DIV
            self._div()
            # print('div')
        elif self._IR & 0xfc0000ff == 0x0000001b:    # DIVU
            self._divu()
            # print('divu')
        elif self._IR & 0xfc0000ff == 0x00000010:    # MFHI
            self._mfhi()
            # print('mfhi')
        elif self._IR & 0xfc0000ff == 0x00000012:    # MFLO
            self._mflo()
            # print('mflo')
        elif self._IR & 0xfc0000ff == 0x00000014:    # LIS
            self._lis()
            # print('lis')
        elif self._IR & 0xfc000000 == 0x8c000000:    # LW
            self._lw()
            # print('lw')
        elif self._IR & 0xfc000000 == 0xac000000:    # SW
            self._sw()
            # print('sw')
        elif self._IR & 0xfc0000ff == 0x0000002a:    # SLT
            self._slt()
            # print('slt')
        elif self._IR & 0xfc0000ff == 0x0000002b:    # SLTU
            self._sltu()
            # print('sltu')
        elif self._IR & 0xfc000000 == 0x10000000:    # BEQ
            self._beq()
            # print('beq')
        elif self._IR & 0xfc000000 == 0x14000000:    # BNE
            self._bne()
            # print('bne')
        elif self._IR & 0xfc0000ff == 0x00000008:    # JR
            self._jr()
            # print('jr')
        elif self._IR & 0xfc0000ff == 0x00000009:    # JALR
            self._jalr()
            # print('jalr')
        else:
            raise ValueError('Unrecognized command of the form 0x' + format(self._IR, '08x'))

    def _add(self):
        s, t, d = self._get_registers()
        self._registers[d] = (self._registers[s] + self._registers[t]) % 2 ** 32

    def _sub(self):
        s, t, d = self._get_registers()
        self._registers[d] = (self._registers[s] - self._registers[t]) % 2 ** 32

    def _mult(self):
        s, t, d = self._get_registers()
        # need to interpret as signed int!
        temp = self._signed(self._registers[s]) * self._signed(self._registers[t])
        self._lo = temp & 0xffffffff
        self._hi = (temp >> 32) & 0xffffffff

    def _multu(self):
        s, t, d = self._get_registers()
        temp = self._registers[s] * self._registers[t]
        self._lo = temp & 0xffffffff
        self._hi = (temp >> 32) & 0xffffffff

    def _div(self):
        s, t, d = self._get_registers()
        # need to interpret as signed int!
        self._lo = (self._signed(self._registers[s]) // self._signed(self._registers[t])) & 0xffffffff
        self._hi = (self._signed(self._registers[s]) % self._signed(self._registers[t])) & 0xffffffff

    def _divu(self):
        s, t, d = self._get_registers()
        self._lo = (self._registers[s] // self._registers[t]) & 0xffffffff
        self._hi = (self._registers[s] % self._registers[t]) & 0xffffffff

    def _mfhi(self):
        s, t, d = self._get_registers()
        self._registers[d] = self._hi

    def _mflo(self):
        s, t, d = self._get_registers()
        self._registers[d] = self._lo

    def _lis(self):
        s, t, d = self._get_registers()
        self._registers[d] = self._memory[self._PC // 4]
        self._PC += 4

    def _lw(self):
        import sys
        s, t, d = self._get_registers()
        i = self._get_immediate()
        address = self._registers[s] + i
        if address % 4 != 0:
            raise ValueError("Unaligned access at address 0x" + format(address, '08x'))
        # if address == 0xffff0004:
        #     self._registers[t] = sys.stdin.buffer.read()
        else:
            self._registers[t] = self._memory[address // 4]

    def _sw(self):
        import sys
        s, t, d = self._get_registers()
        i = self._get_immediate()
        address = self._registers[s] + i
        if address % 4 != 0:
            raise ValueError("Unaligned access at address 0x" + format(address, '08x'))
        # if address == 0xffff000c:
        #     sys.stdout.buffer.write(self._registers[t] & 0xff)
        else:
            self._memory[address // 4] = self._registers[t]

    def _slt(self):
        s, t, d = self._get_registers()
        s_val = self._signed(self._registers[s])
        t_val = self._signed(self._registers[t])
        if s_val < t_val:
            self._registers[d] = 1
        else:
            self._registers[d] = 0

    def _sltu(self):
        s, t, d = self._get_registers()
        if self._registers[s] < self._registers[t]:
            self._registers[d] = 1
        else:
            self._registers[d] = 0

    def _beq(self):
        s, t, d = self._get_registers()
        i = self._get_immediate()
        if self._registers[s] == self._registers[t]:
            self._PC += i * 4

    def _bne(self):
        s, t, d = self._get_registers()
        i = self._get_immediate()
        if self._registers[s] != self._registers[t]:
            self._PC += i * 4

    def _jr(self):
        s, t, d = self._get_registers()
        if self._registers[s] % 4 != 0:
            raise ValueError("Unaligned jump at address 0x" + format(self._registers[s], '08x'))
        if self._registers[s] == 0xfffffffc:
            # Default $31 value means return
            self._end()
        else:
            self._PC = self._registers[s]

    def _jalr(self):
        s, t, d = self._get_registers()
        if self._registers[s] % 4 != 0:
            raise ValueError("Unaligned jump at address 0x" + format(self._registers[s], '08x'))
        if self._registers[s] == 0xfffffffc:
            # Default $31 value means return
            self._end()
        else:
            self._PC, self._registers[31] = self._registers[s], self._PC

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
            print("$" + str(i*4).zfill(2) + " = 0x" + format(self._registers[i * 4], '08x'), end='   ')
            print("$" + str(i*4+1).zfill(2) + " = 0x" + format(self._registers[i * 4 + 1], '08x'), end='   ')
            print("$" + str(i*4+2).zfill(2) + " = 0x" + format(self._registers[i * 4 + 2], '08x'), end='   ')
            print("$" + str(i*4+3).zfill(2) + " = 0x" + format(self._registers[i * 4 + 3], '08x'))
        print(" PC = 0x" + format(self._PC, '08x'))

    def _get_registers(self):
        """
        From the IR, gets the registers S, T and D
        Returns in the form (S, T, D)
        :return: Tuple(int, int, int)
        """
        # bit mask and shift
        s = (self._IR & 0x03E00000) >> 21
        t = (self._IR & 0x001F0000) >> 16
        d = (self._IR & 0x0000F800) >> 11
        return s, t, d

    def _get_immediate(self):
        """
        From the IR, gets the immediate value i
        :return: int
        """
        # bit mask
        imm = self._IR & 0x0000ffff
        if imm < 2**15:
            return imm
        return imm - 2**16

    def _breakpoint_reached(self):
        while True:
            inpt = input('Command (n - next line, c - continue, p - print): ')
            if inpt.lower() in {'n', 'next'}:
                self._break = True
                return
            elif inpt.lower() in {'c', 'continue'}:
                self._break = False
                return
            elif inpt.lower() in {'p', 'print'}:
                self._print()
                print(" IR = 0x" + format(self._IR, '08x'))
            else:
                print('Command not recognized: ' + inpt)

    def run(self):
        self._initialize()
        print("Running MIPS program.")
        while True:
            self._registers[0] = 0
            if self._PC in self._breakpoints or self._break:
                self._breakpoint_reached()
            self._IR = self._memory[self._PC // 4]
            self._PC += 4
            self._execute()


def open_file():
    file_name = input('Enter filename: ')
    try:
        file = open(file_name, 'rb')
        return file
    except OSError:
        print("Could not open file")
        exit(-1)

def get_debug_mode():
    inpt = input('Debug mode? (Y/N): ')
    if inpt.lower() in {'y', 'yes'}:
        return True
    return False

def get_breakpoints():
    inpt = input('Enter all breakpoints separated by spaces: ')
    bp = set([int(x)*4 for x in inpt.split()])
    return bp


print("##### CS-241 MIPS emulator #####")
mips = MIPS_machine()
mips.run()

# TODO: figure out get_char() and put_char() equivalent for Python

