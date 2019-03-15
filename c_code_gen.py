import os
import sys
import logging

indentChar = ' '

class Code():
    def __init__(self):
        self.elements = []

    def __str__(self):
        result = []
        for e in self.elements:
            if e is None:
                result.append('')
            else:
                result.append(str(e))
            if not isinstance(e, Blank):
                result.append('\n')
        return ''.join(result)

    def __len__(self):
        return len(self.elements)

    def append(self, element):
        self.elements.append(element)

    def extend(self, element):
        self.elements.extend(element)

    def lines(self):
        lines = []
        for e in self.elements:
            if hasattr(e, 'lines') and callable(e.lines):
                lines.extend(e.lines())
            else:
                lines.extend(str(e).split('\n'))
        return lines

class _File(object):
    def __init__(self, path):
        self.path = path
        self.code = Code()

    def generate(self):
        with open(self.path, 'w') as f:
            f.write(str(self.code))

class CFile(_File):
    def __init__(self, path):
        super().__init__(path)

    def __str__(self):
        return str(self.code)

    def lines(self):
        return self.code.lines()

class HFile(_File):
    def __init__(self, path):
        super().__init__(path)
        _basename = os.path.basename(self.path)
        _splitname = os.path.splitext(_basename)[0].upper()
        self.guard = "__" + _splitname + "_H__"

    def __str__(self):
        _str = ''
        _str += str(Ifndef(self.guard))
        _str += str(Define(self.guard))
        _str += str(self.code)
        _str += str(Endif())
        return _str

    def set_guard(self, guard):
        self.guard = guard

class Block():
    def __init__(self):
        self.code = Code()
        self.tail = ''

    def __str__(self):
        _str = '{\n'
        _lines = []
        for e in self.code.elements:
            _lines.append(str(e))
        _str += '\n'.join(_lines) + '\n'
        _str += '}' + '%s' % (self.tail)
        return _str

    def append(self, element):
        self.code.append(element)

    def extend(self, code):
        self.code.extend(code)

    def lines(self):
        lines = []
        lines.append('{')
        for e in self.code.elements:
            lines.append(str(e))
        lines.append('}%s' % self.tail)
        return lines

class Ifndef():
    def __init__(self, text):
        self.text = "#ifndef " + text + '\n'

    def __str__(self):
        return self.text

class Endif():
    def __str__(self):
        return "#endif"

class Define():
    def __init__(self, text):
        self.text = "#define " + text + '\n'

    def __str__(self):
        return str(self.text)

class Blank():
    def __init__(self, lines=1):
        self.lines = lines

    def __str__(self):
        return '\n' * self.lines

    def lines(self):
        return ['' for x in range(self.lines)]

class Variable():
    def __init__(self, type, name, initialization=None):
        self.type = type
        self.name = name
        self.initialization = initialization

    def __str__(self):
        if self.initialization is None:
            return str(self.type + ' ' + self.name)
        else:
            return str(self.type + ' ' + self.name) + '=' + str(self.initialization)

    def setprefix(self, prefix):
        self.type = str(prefix) + ' ' +self.type

    def isvalidtype(self, type):
        types = ('char',
                 'signed char',
                 'unsigned char',
                 'short',
                 'short int',
                 'signed short',
                 'signed short int',
                 'unsigned short',
                 'unsigned short int',
                 'int',
                 'signed',
                 'signed int',
                 'unsigned',
                 'unsigned int',
                 'long',
                 'long int',
                 'signed long',
                 'signed long int',
                 'unsigned long',
                 'unsigned long int',
                 'long long',
                 'long long int',
                 'signed long long',
                 'signed long long int',
                 'unsigned long long',
                 'unsigned long long int',
                 'float',
                 'double',
                 'long double'
                 )
        return type in types

class Array(Variable):
    def __init__(self, type, name, *args):
        if super().isvalidtype(type) is False:
            logging.error('wrong type : %s', str(type))
            exit(-1)
        super().__init__(type, name)
        self.index = 0
        self.data = []
        for a in args:
            self.data.append(str(a))

    def __str__(self):
        return super().__str__() + '[' + str(len(self.data)) + '] = {' + ','.join(self.data) + '}'

    def add(self, value):
        self.data.append(str(value))

class Pointer(Variable):
    def __init__(self, type, name, initialization=None):
        if super().isvalidtype(type) is False:
            logging.error('wrong type : %s', str(type))
            exit(-1)
        super().__init__(type, name, initialization)

    def __str__(self):
        _str = super().__str__().split()
        _str.insert(1, '* ')
        return str(''.join(_str))

class Typedef:
    def __init__(self, base, definition):
        self.base = base
        self.definition = definition

    def __str__(self):
        return 'typedef %s %s' % (str(self.base), str(self.definition))

class Struct:
    def __init__(self, name, block=None):
        self.block = block if block is not None else Block()
        self.name = name

    def __str__(self):
        return '\n'.join(self.lines())

    def append(self, type, name):
        self.block.append('%s %s' % (type, name))

    def append_list(self, list):
        for type, name in list:
            self.append(type, name)

    def lines(self):
        lines = []
        lines.append('struct %s' % (self.name))
        lines.extend(self.block.lines())
        return lines

class Enum:
    def __init__(self, name, block=None):
        self.block = block if block is not None else Block()
        self.name = name

    def __str__(self):
        return '\n'.join(self.lines())

    def append(self, value):
        self.block.append(str(value))

    def append_with_init(self, value, init):
        self.append('%s = %s' % value, init)

    def lines(self):
        lines = []
        lines.append('enum %s' % self.name)
        lines.extend(self.block.lines())
        return lines

class Statement:
    def __init__(self, state):
        self.state = state
    def __str__(self):
        return str(self.state) + ';'

class Include:
    def __init__(self, header, system=False):
        self.header = header
        self.system = system

    def __str__(self):
        if self.system == True:
            return '#include <%s>' % self.header
        else:
            return '#include "%s"' % self.header

class ForIter:
    def __init__(self, init='', expression='', increment='', block=None):
        self.iter = 'for (%s;%s;%s)' % (init, expression, increment)
        self.block = block if block is not None else Block()

    def __str__(self):
        _str = ''
        _str += self.iter
        _str += str(self.block)
        return _str

    def addline(self, line):
        self.block.append(line)

    def setblock(self, block):
        self.block = block

    def lines(self):
        lines = []
        lines.append(self.iter)
        lines.append(self.block.lines())
        return lines

class _IfElse():
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

class IfStatement:
    def __init__(self, condition, block):
        self.else_statement = None

        _if = _IfElse(condition, block)
        self.statements = []
        self.statements.append(_if)

    def __str__(self):
        _str = ''
        if_state = self.statements[0]
        _str += 'if (%s) ' % if_state.condition
        _str += str(if_state.block) + '\n'
        for elif_state in self.statements[1:]:
            _str += 'else if (%s) ' % elif_state.condition
            _str += str(elif_state.block) + '\n'
        if self.else_statement is not None:
            _str += 'else ' + str(self.else_statement)
        return _str

    def append_elif(self, condition, block):
        _if = _IfElse(condition, block)
        self.statements.append(_if)

    def set_else(self, block):
        self.else_block = block

    def lines(self):
        lines = []
        lines.append('')

class Function:
    def __init__(self, name, ret_type, parameters=None, block=None):
        self._name = name
        self._ret_type = ret_type
        self._parameters = [] if parameters is None else list(parameters)
        self._block = block if block is not None else Block()
        self._static = False

    def __str__(self):
        _str = ''
        _str += 'static ' if self.static is True else ''

        _str += '%s %s(%s) \n' % (self._ret_type, self._name, ', '.join(self._parameters))
        _str += str(self._block)
        return _str

    @property
    def static(self):
        return self._static

    @static.setter
    def static(self, value:bool):
        if isinstance(value, bool) is False:
            raise ValueError('static property expect bool type')
        self._static = value

    def add_parameter(self, parameters):
        self._parameters.extend(parameters)

    @property
    def block(self):
        return self._block

    @block.setter
    def block(self, block):
        if isinstance(block, Block) is False:
            raise ValueError('block property expect Block object')
        self._block = block

    def addline(self, line):
        self._block.append(line)


class FuncCall():
    def __init__(self, name, args=None):
        self._name = name
        self._args = [] if args is None else list(args)

    def __str__(self):
        _str = '%s(%s)' % (self._name, ', '.join(str(x) for x in self._args))
        return _str


if __name__ == '__main__':
    cfile = CFile('test.ct')
    code = cfile.code

    #header
    code.append(Include('stdio.h', True))

    block = Block()
    block.append(Statement('return 1'))
    if1 = IfStatement('a > b', block)
    if1.append_elif('a == b', block)
    code.append(if1)
    iter = ForIter('a = 1', 'a < 10', 'a++')
    iter.addline(Statement('code = 0'))
    code.append(iter)

    code.append(Blank(5))

    func = Function('func', 'int')
    func.block = Block()
    func.static = True
    func.add_parameter(['int a', 'int b'])
    func.block.append(Statement('return 0'))

    fc = FuncCall('func', ['a, b, d'])
    code.append(func)

    code.append(Statement(fc))


    print(cfile)
