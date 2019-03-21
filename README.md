# C_CodeGen


```python
import c_code_gen as cg

cfile = cg.CFile('test.c')
c_code = cfile.code

c_code.append(cg.Include('stdio.h', True))

main_func = c_code.Function('main', 'int')
main_func.block = cg.Block()
main_func.block.append(Statement(Variable('int', 'a')))
main_func.block.append(Statement('a = 10')
main_func.block.append(FuncCall('printf', '"a is %d\n"', 'a')

c_code.append(main_func)

cfile.generator()

```
