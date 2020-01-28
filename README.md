# ccodegen

### How to install

```bash
pip install ccodegen
```

### Example

This is a ccodegen package. 

#### Code
```python
import ccodegen as cg

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

#### Result : test.c
```c
#include <stdio.h>

int main()
{
int a;
a = 10;
printf('a is %d/\n', a);
}

```
