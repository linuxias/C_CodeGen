import sys
import c_code_gen as cg

def check_version():
    try:
        assert sys.version_info >= (3, 5)
    except AssertionError:
        print('Python version is too low: ', sys.version_info, file=sys.stderr)
        print('Minimum required version: 3.5', file=sys.stderr)
        sys.exit(-1)

if __name__ == '__main__':
    check_version()

    cfile = cg.CFile('test.c')
    cfile.add_include(cg.Include('stdio.h', True))

    c_code = cfile.code

    main_func = cg.Function('main', 'int')
    main_func.block = cg.Block()
    main_func.block.append(cg.Statement(cg.Variable('int', 'a')))
    main_func.block.append(cg.Statement('a = 10'))
    main_func.block.append(cg.FuncCall('printf', [repr("a is %d\n"), 'a']))
    c_code.append(main_func)
    cfile.generate()
