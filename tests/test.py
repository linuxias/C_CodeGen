import os
import unittest
import ccodegen as cg

class TestCodeGen(unittest.TestCase):
    def test_ifndef(self):
        tmp = cg.Ifndef('__TEST_H__')
        self.assertEqual(str(tmp), '#ifndef __TEST_H__\n')

    def test_endif(self):
        self.assertEqual(str(cg.Endif()), '#endif')

    def test_cfile(self):
        cfile = cg.CFile('test.c')
        cfile.add_include('stdio.h')
        cfile.add_include('stdlib.h')
        cfile.generate()

if __name__ == '__main__':
    unittest.main()
