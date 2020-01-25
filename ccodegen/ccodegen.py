import os
import re

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
        return self

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
            f.write(str(self))

class CFile(_File):
    def __init__(self, path):
        super().__init__(path)
        self.include = []
        self.extern = []

    def add_include(self, include):
        self.include.append(include)

    def add_extern(self, extern):
        self.extern.append(extern)

    def __str__(self):
        _str = ''
        for _include in self.include:
            _str += '#include <' + _include.__str__() + '>\n'
        _str += '\n'

        for _extern in self.extern:
            _str += 'extern ' + _extern.__str__() + '\n'
        _str += '\n'

        _str += str(self.code)
        _str += '\n'
        return _str

    def lines(self):
        return self.code.lines()

class HFile(_File):
    def __init__(self, path):
        super().__init__(path)
        _basename = os.path.basename(self.path)
        _splitname = os.path.splitext(_basename)[0]
        _guard = re.findall('[A-Z][^A-Z]*', _splitname)
        self.guard = '__' + '_'.join(_guard).upper() + '_H__'

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


class Array(Variable):
    def __init__(self, type, name, *args):
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
        self._typedef = False

    def __str__(self):
        _str = ''
        _suffix = ''
        if self._typedef is True:
            _str += 'typedef struct {\n'
            _suffix = self.name
        else:
            _str += 'struct %s {\n' % (self.name)
        _str += ';\n'.join(self.block.code.lines())
        _str += ';\n} %s' % (_suffix)
        return _str

    @property
    def typedef(self):
        return self._typedef

    @typedef.setter
    def typedef(self, set: bool):
        self._typedef = set

    def append(self, value):
        if isinstance(value, list):
            self.append_list(value)
        else:
            self.block.append('%s' % value)

    def append_list(self, value_list):
        for value in value_list:
            self.append(value)


class Union:
    def __init__(self, name, block=None):
        self._block = block if block is not None else Block()
        self._name = name
        self._typedef = False

    def __str__(self):
        _str = ''
        _suffix = ''
        if self._typedef is True:
            _str += 'typedef union {\n'
            _suffix = self.name
        else:
            _str += 'union %s {\n' % (self.name)
        _str += ';\n'.join(self.block.code.lines())
        _str += ';\n} %s' % (_suffix)
        return _str

    @property
    def typedef(self):
        return self._typedef

    @typedef.setter
    def typedef(self, set: bool):
        self._typedef = set

    def append(self, value):
        self.block.append(value)

    def append(self, type, name):
        self.block.append(str(type) + ' ' + str(name))


class Enum:
    def __init__(self, name, block=None):
        self.block = block if block is not None else Block()
        self.name = name
        self._typedef = False

    def __str__(self):
        _str = ''
        _suffix = ''
        if self._typedef is True:
            _str += 'typedef enum {\n'
            _suffix = self.name
        else :
            _str += 'enum %s {\n' % (self.name)
        _str += ',\n'.join(self.block.code.lines())
        _str += '\n} %s' % (_suffix)
        return _str

    @property
    def typedef(self):
        return self._typedef

    @typedef.setter
    def typedef(self, set: bool):
        self._typedef = set

    def append(self, value):
        self.block.append(str(value))

    def append_with_init(self, value, init):
        self.append('%s = %s' % (value, init))

        
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

class Extern:
    def __init__(self, extern):
        self.extern = extern

    def __str__(self):
        return 'extern ' + str(self.extern) +';'

class ForIter:
    def __init__(self, init='', expression='', increment='', block=None):
        self.iter = 'for(%s;%s;%s)' % (init, expression, increment)
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
        self.else_statement = block

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
        _str += '\n'
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
        _str = '%s(%s);' % (self._name, ', '.join(str(x) for x in self._args))
        return _str

    def add_arg(self, arg):
        self._args.append(arg)

class Switch():
    def __init__(self, arg, block = None):
        self._arg = arg
        self._block = block if block is not None else Block()
        self._case = []

    def __str__(self):
        _str = ''
        _str += 'switch(%s)\n'% self._arg + '{'
        for _case in self._case:
            _str += _case.__str__()
        _str += '}'
        return _str

    def add_case(self, case):
        self._case.append(case)

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

class Case():
    def __init__(self, arg, code=None):
        self._arg = arg
        self._code = code if code is not None else Code()

    def __str__(self):
        _str = ''
        _str += 'case %s:\n'% self._arg
        _str += str(self._code)
        _str += 'break;\n\n'
        return _str

    @property
    def block(self):
        return self._block

    def addline(self, line):
        self._code.append(line)

