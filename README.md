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
cfile.add_include(cg.Include('stdio.h', True))

c_code = cfile.code

main_func = cg.Function('main', 'int')
main_func.block = cg.Block()
main_func.block.append(cg.Statement(cg.Variable('int', 'a')))
main_func.block.append(cg.Statement('a = 10'))
main_func.block.append(cg.FuncCall('printf', [repr("a is %d\n"), 'a']))
c_code.append(main_func)
cfile.generate()

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
