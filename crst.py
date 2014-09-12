from __future__ import division
from __future__ import print_function
import os
import tabulate
import codecs
import locale
import oncepy
import oncepy.oconfig as cfg
from oncepy import ccheck
from oncepy import oconfig as cfg
from numpy import *
from numpy import linalg as LA
from sympy import *
from sympy import var as varsym
from sympy.core.alphabets import greeks

mpathcrst = os.getcwd()
try:
    from unitc import *
    cfg.unitfile = 'model folder'
except ImportError:
    try:
        os.chdir(os.pardir)
        from unitc import *
        cfg.unitfile = 'project folder'
        os.chdir(mpathcrst)
    except ImportError:
        from oncepy.unitc import *
        cfg.unitfile = 'built-in'
os.chdir(mpathcrst)


class CalcRST(object):
    """Accepts a model dictionary and writes an rst file"""

    def __init__(self, odict, fidict):
        """initialize files

        **Args**
        odict (dict)

        Keys for equations and terms are the dependent
        variable. Keys for other operations are generated by a
        line counter.

        For non-equation entries the dictionary key is:
        _i + incremented number - file operation
        _s + incremented number - sections
        _y + incremented number - symbolic representation
        _t + incremented number - inserted text
        _c + incremented number - check operation
        _a + incremented number - array and ranges
        _f + incremented number - function
        _x + incremented number - pass-through text
        _m + incremented number - current model directory
        _pd - license text

        the dictionary structure is:
        single line inputs:
        file:     [[i], refnum, description, mod number]
        sections: [[s], left string, notes]
        symbolic: [[y], expr]
        terms:    [[t], statement, expr, ref ]

        internal:
        blank line: [~]
        text:       [[x], text]
        read data   [[rd], var = data]

        multiline inputs
        check:    [[c], check expr, limits, ref, ok]
        arrays:   [[a], state1, expr, range1, range2, ref, dec, u1, u2]
        function: [[f], function call, var, ref, eq num]
        equations:[[e], statement, expr, ref, decimals, units, prnt opt]

        """
        # execution log
        self.ew = ccheck.ModCheck()

        # dicts and lists
        self.odict = odict
        self.fidict = fidict
        self.symb = self.odict.keys()
        self.symblist = []


        #paths and files
        self.mpath = cfg.mpath
        self.mfile = cfg.mfile
        #print('mfile', self.mfile)
        self.rfilename = self.mfile.replace('.txt', '.rst')
        self.rpath = os.path.join(self.mpath, self.rfilename)
        #print('rpath', self.rpath)
        self.rf1 = codecs.open(self.rpath, 'w', encoding='utf8')

        # parameters
        self.prfilename = ''
        self.previous = ''
        self.xtraline = False
        self.fignum = 0
        self.widthp = 70   # line width

    def gen_rst(self):
        """ write rst file """

        termbegin = 1 # avoid extra lines in term lists
        mtagx = ''
        for _i in self.odict:
            #print(_i, self.odict[_i])
            mtag = self.odict[_i][0]
            if mtagx == '[t]':
                if mtag == '[t]':
                    termbegin = 0
            if mtagx == '[t]':
                if mtag != '[t]':
                    termbegin = 1
                    print('  ', file=self.rf1)
            mtagx = mtag

            if self.odict[_i][1].strip() == '#page':
                print(' ', file=self.rf1)
                print(".. raw:: latex", file=self.rf1)
                print(' ', file=self.rf1)
                print('  \\newpage', file=self.rf1)
                print(' ', file=self.rf1)

            if mtag ==   '[i]':
                self._rst_file(self.odict[_i])
                self.xtraline = True
            elif mtag == '[s]':
                self._rst_sect(self.odict[_i])
            elif mtag == '[y]':
                self._rst_sym(self.odict[_i])
                self.xtraline = False
            elif mtag == '[t]':
                self._rst_term(self.odict[_i], termbegin)
                self.xtraline = False
            elif mtag == '[c]':
                self._rst_check(self.odict[_i])
                self.xtraline = True
            elif mtag == '[a]':
                self._rst_array(self.odict[_i])
                self.xtraline = True
            elif mtag == '[f]':
                self._rst_func(self.odict[_i])
                self.xtraline = False
            elif mtag == '[e]':
                self._rst_eq(_i, self.odict[_i])
                self.xtraline = False
            elif mtag == '[x]':
                self._rst_txt(self.odict[_i])
                self.xtraline = True
            else:
                pass

            if mtag == '[~]' and self.xtraline is False:
                self.xtraline = True
            if mtag == '[~]' and self.xtraline is True:
                self._rst_blnk()

        for i2 in self.odict:                       # add calc license
            if i2 == '_pd':
                self._rst_txt(['[pd]', self.odict[i2]])

        self._rst_blnk()
        self._rst_txt([' ','\n**[end of calc]**'])  # end calc
        self.rf1.close()                            # close rst file
        #for i in self.odict: print(i, self.odict[i])

    def _rst_sect(self, dval):
        """print section

        Dictionary:
        section: ['[s]', sleft, file]

        """
        tleft = dval[1].strip()
        tright = dval[2].strip()
        print('  ', file=self.rf1)
        print(tleft.strip() + "aa-bb " + tright.strip(),
              file=self.rf1)
        print("-"*self.widthp, file=self.rf1)
        print(' ', file=self.rf1)
        print(".. raw:: latex", file=self.rf1)
        print(' ', file=self.rf1)
        print('   \\vspace{1mm}', file=self.rf1)
        print(' ', file=self.rf1)

    def _rst_sym(self, dval):
        """print symbolic representation

        Dictionary:
        symbolic:[[l], expr]

        """
        dval = dval[1].replace('=', '<=')
        exp2 = dval.split('\n')
        exp3 = ' '.join([ix.strip() for ix in exp2])
        symp1 = sympify(exp3)

        for _j in symp1.atoms():
            varsym(str(_j))

        symeq = eval(dval)
        # symbolic repr
        print('  ', file=self.rf1)
        print('.. math:: ', file=self.rf1)
        print('  ', file=self.rf1)
        print('  ' + latex(symeq, mul_symbol="dot"), file=self.rf1)
        print('  ', file=self.rf1)
        print('|', file=self.rf1)
        print('  ', file=self.rf1)

    def _rst_term(self, dval, termbegin):
        """print terms

        terms: [[t], statement, expr, ref ]

        """
        ptype = type(eval(dval[2]))
        val1 = eval(dval[2].strip())
        var1 = dval[1].split('=')[0].strip()

        state = var1 + ' = ' + str(val1)
        shift = int(self.widthp / 2.0)
        ref = dval[3].strip().ljust(shift)
        termpdf = " "*4 + ref + ' | ' + state

        if ptype == ndarray or ptype == list or ptype == tuple:
            termpdf = '. ' + ref + ' | ' + var1 + ' = ' + '\n'


        if ptype == ndarray:
            tmp1 = str(val1)
            if '[[' in tmp1:
                tmp2 = tmp1.replace(' [', '.  [')
                tmp1 = tmp2.replace('[[', '. [[')
            else:
                tmp1 = tmp1.replace('[', '. [')
            print('  ', file=self.rf1)
            print('::', file=self.rf1)
            print('  ', file=self.rf1)
            print(termpdf, file=self.rf1)
            print(tmp1, file=self.rf1)
            print('  ', file=self.rf1)
            print(".. raw:: latex", file=self.rf1)
            print('  ', file=self.rf1)
            print('   \\vspace{1mm}', file=self.rf1)
            print('  ', file=self.rf1)
            return

        elif ptype == list or ptype == tuple:
            tmp1 = str(val1)
            if ']]' in tmp1:
                tmp1 = tmp1.replace(']]', ']]\n')
            else:
                tmp1 = tmp1.replace(']', ']\n')
            print('  ', file=self.rf1)
            print('::', file=self.rf1)
            print('  ', file=self.rf1)
            print(termpdf, file=self.rf1)
            print(tmp1, file=self.rf1)
            print('  ', file=self.rf1)
            print(".. raw:: latex", file=self.rf1)
            print('  ', file=self.rf1)
            print('   \\vspace{1mm}', file=self.rf1)
            print('  ', file=self.rf1)
            return

        if termbegin:
            #print('termbegin')
            print('  ', file=self.rf1)
            print('::', file=self.rf1)
            print('  ', file=self.rf1)

        print(termpdf, file=self.rf1)

    def _rst_check(self, dval):
        """print check

        Dictionary:
        check:  [[c], check expr, op, limit, ref, dec, ok]

        """

        try:
            exec("set_printoptions(precision=" + dval[5].strip() + ")")
            exec("Unum.VALUE_FORMAT = '%." + dval[5].strip() + "f'")
        except:
            set_printoptions(precision=3)
            Unum.VALUE_FORMAT = "%.3f"

        # convert variables to symbols
        for _j in self.symb:
            if _j[0] != '_':
                varsym(_j)

        # symbolic form
        symeq1 = eval(dval[1].strip() + dval[2].strip() +
                      dval[3].strip())
        #pprint(symeq1)
        # evaluate variables
        for _k in self.odict:
            if _k[0] != '_':
                #print(self.odict[_k][1].strip())
                exec(self.odict[_k][1].strip())

        # substitute values
        try:
            nounits1 = eval(dval[1].strip()).asNumber()
        except:
                nounits1 = eval(dval[1].strip())
        try:
            nounits2 = eval(dval[3].strip()).asNumber()
        except:
                nounits2 = eval(dval[3].strip())

        result = eval(str(nounits1) + dval[2].strip() + str(nounits2))
        resultform = '{:.' + dval[5].strip()+'f}'
        result1 = resultform.format(float(str(nounits1)))
        result2 = resultform.format(float(str(nounits2)))
        subbed = result1 + ' ' + dval[2].strip() + ' ' + result2

        if result:
            comment = ' - ' + dval[6].strip()
        else:
            comment = ' *** not ' + dval[6].strip() + ' ***'
        out2p = subbed + '  ' + comment

        # section header
        secthead = dval[4].strip()
        # equation label
        print("aa-bb " + "**" + secthead + "**", file=self.rf1)
        print('  ', file=self.rf1)

        # draw horizontal line
        print(".. raw:: latex", file=self.rf1)
        print('  ', file=self.rf1)
        print('   \\vspace{-1mm}', file=self.rf1)
        print('  ', file=self.rf1)
        print('   \\hrulefill', file=self.rf1)
        print('  ', file=self.rf1)

        # symbolic repr
        print('  ', file=self.rf1)
        print('.. math:: ', file=self.rf1)
        print('  ', file=self.rf1)
        print('  ' + latex(symeq1, mul_symbol="dot"), file=self.rf1)
        print('  ', file=self.rf1)
        print('|', file=self.rf1)
        print('  ', file=self.rf1)

        # substituted values in equation
        # list of symbols
        symat = symeq1.atoms(Symbol)

        # convert to latex form
        latexrep = latex(symeq1, mul_symbol="dot")
        #print('latex', latexrep)

        switch1 = []
        # rewrite equation with braces
        for _n in symat:
            newlatex1 = str(_n).split('__')
            if len(newlatex1) == 2:
                newlatex1[1] += '}'
                newlatex1 = '~d~'.join(newlatex1)

            newlatex1 = str(_n).split('_')
            if len(newlatex1) == 2:
                newlatex1[1] += '}'
                newlatex1 = '~s~'.join(newlatex1)

            newlatex1 = ''.join(newlatex1)
            newlatex1 = newlatex1.replace('~d~', '__{')
            newlatex1 = newlatex1.replace('~s~', '_{')
            symeq1 = symeq1.subs(_n, symbols(newlatex1))
            switch1.append([str(_n), newlatex1])
        # list of new symbols

        # substitute values
        for _n in switch1:
            expr1 = eval((self.odict[_n[0]][1]).split("=")[1])
            if type(expr1) == float:
                form = '{:.' + dval[5].strip() +'f}'
                symvar1 = '{' + form.format(expr1) + '}'
            else:
                symvar1 = '{' + str(expr1) + '}'
            latexrep = latexrep.replace(_n[1], symvar1)
            latexrep = latexrep.replace("\{", "{")


        # add substituted equation to rst file
        print('  ', file=self.rf1)
        print('.. math:: ', file=self.rf1)
        print('  ', file=self.rf1)
        print('  ' + latexrep, file=self.rf1)
        print('  ', file=self.rf1)
        print('|', file=self.rf1)
        print('  ', file=self.rf1)

        # result
        print(' ', file=self.rf1)
        print('.. math:: ', file=self.rf1)
        print('  ', file=self.rf1)
        print("  \\boldsymbol{" + latex(out2p,
                mode='plain') + "}", file=self.rf1)
        print('  ', file=self.rf1)


    def _rst_array(self, dval):
        """
        print tag [a] - an ascii table from statements or variable

        arrays:   [[a], statement, expr, range1, range2,
        ref, decimals, unit1, unit2, model]

        """
        try:
            eformat, rformat = dval[4].split(',')
            exec("set_printoptions(precision=" + eformat + ")")
            exec("Unum.VALUE_FORMAT = '%." + eformat + "f'")
        except:
            eformat = '3'
            rformat = '3'
            set_printoptions(precision=3)
            Unum.VALUE_FORMAT = "%.3f"

        # table heading
        vect = dval[1:]
        tright = dval[5].strip().split(' ')
        eqnum = tright[-1].strip()
        tleft = ' '.join(tright[:-1]).strip()
        tablehdr = tleft + ' ' + eqnum
        print("aa-bb " + "**" + tablehdr + "**", file=self.rf1)

        # print symbolic form
        # convert variables to symbols except for arrays
        try:
            for _j in self.symb:
                if str(_j)[0] != '_':
                    varsym(str(_j))

            #convert array variable
            var1 = vect[2].split('=')[0].strip()
            varsym(str(var1))
            try:
                var2 = vect[3].split('=')[0].strip()
                varsym(str(var2))
            except:
                pass
            try:
                symeq = latex(eval(vect[1].strip()))
                var0 = latex(vect[0].split('=')[0])
                symeq1 = var0 + ' = ' + symeq
            except:
                symeq = vect[1].strip()
                var0 =  vect[0].split('=')[0]
                symeq1 = var0 + ' = ' + symeq
            #print('latex', symeq1)

            etype = vect[0].split('=')[1]
            if etype.strip()[:1] == '[':
                out1 = str(vect[0].split('=')[1])

            # symbolic repr
            print('  ', file=self.rf1)
            print('.. math:: ', file=self.rf1)
            print('  ', file=self.rf1)
            print('  ' + latex(symeq1, mul_symbol="dot"), file=self.rf1)
            print('  ', file=self.rf1)
            print('|', file=self.rf1)
            print('  ', file=self.rf1)
        except:
            pass

        # evaluate variables - strip units for arrays
        for k1 in self.odict:
            #print('k1', k1)
            if k1[0] != '_':
                    try:
                        exec(self.odict[k1][1].strip())
                    except:
                        pass
                    try:
                        state = self.odict[k1][1].strip()
                        varx = state.split('=')
                        state2 = varx[0].strip()+'='\
                        +varx[0].strip() + '.asNumber()'
                        exec(state2)
                        #print('j1', k1)
                    except:
                        pass
            if k1[0:2] == '_a':
                #print('k1-2', k1)
                try:
                    exec(self.odict[k1][3].strip())
                    exec(self.odict[k1][4].strip())
                    exec(self.odict[k1][1].strip())
                except:
                    pass
        # single row vector - 1D table
        if len(str(vect[3])) == 0 and len(str(vect[0])) != 0:
            # process range variable 1 and heading
            rnge1 = vect[2]
            exec(rnge1.strip())
            rnge1a = rnge1.split('=')
            rlist = [vect[6].strip() + ' = ' +
                     str(_r)for _r in eval(rnge1a[1])]
            #process equation
            equa1 = vect[0].strip()
            #print(equa1)
            exec(equa1)
            var2 = equa1.split('=')[0]
            etype = equa1.split('=')[1]
            elist1 = eval(var2)
            if etype.strip()[:1] == '[':
                # data is in list form
                elist2 = []
                alist1 = eval(equa1.split('=')[1])
                for _v in alist1:
                        try:
                            elist2.append(list(_v))
                        except:
                            elist2.append(_v)
            else:
                try:
                    elist2 = elist1.tolist()
                except:
                    elist2 = elist1

            elist2 = [elist2]

            # create 1D table
            ptable = tabulate.tabulate(elist2, rlist, 'rst',
                                floatfmt="."+dval[6].strip()+"f")
            print(ptable, file=self.rf1)
            print('  ', file=self.rf1)
            #print(ptable)

        # 2D table
        if len(str(vect[3])) != 0 and len(str(vect[0])) != 0:
            # process range variable 1
            rnge1 = vect[2]
            exec(rnge1.strip())
            rnge1a = rnge1.split('=')
            rlist = [vect[6].strip() + ' = ' +
                     str(_r) for _r in eval(rnge1a[1])]

            # process range variable 2
            rnge2 = vect[3]
            exec(rnge2.strip())
            rnge2a = rnge2.split('=')
            clist = [str(_r).strip() for _r in eval(rnge2a[1])]
            rlist.insert(0, vect[7].strip())

            # process equation
            equa1 = vect[0].strip()
            #print('equa1', equa1)
            exec(equa1)
            etype = equa1.split('=')[1]
            if etype.strip()[:1] == '[':
                # data is in list form
                alist = []
                alist1 = eval(equa1.split('=')[1])
                #print('alist1', alist1)
                for _v in alist1:
                    for _x in _v:
                        #print('_x', _x)
                        alist.append(list(_x))
                        #print('append', alist)
            else:
                # data is in equation form
                equa1a = vect[0].strip().split('=')
                equa2 = equa1a[1]
                rngx = rnge1a[1]
                rngy = rnge2a[1]
                ascii1 = rnge1a[0].strip()
                ascii2 = rnge2a[0].strip()

                # format table
                alist = []
                for _y12 in eval(rngy):
                    alistr = []
                    for _x12 in eval(rngx):
                        eq2a = equa2.replace(ascii1, str(_x12))
                        eq2b = eq2a.replace(ascii2, str(_y12))
                        el = eval(eq2b)
                        alistr.append(el)
                    alist.append(alistr)
                    #print('append', alist)

            for _n, _p in enumerate(alist):
                _p.insert(0, clist[_n])

            # create 2D table
            flt1 = "." + eformat.strip() + "f"
            #print(alist)
            ptable = tabulate.tabulate(alist, rlist, 'rst',
                                       floatfmt=flt1)
            print(ptable, file=self.rf1)
            print('  ', file=self.rf1)

    def _rst_func(self, dval):
        """print function

        Dictionary:

        Arguments:
        ip: a model line or block

        Dictionary Value:
        function:[[f], function name, var, ref, eqn number

        """
        # print reference line

        funcdescrip = dval[3].split(']')[1]
        funchd = funcdescrip.strip() + ' ' + dval[4].strip()

        # insert pattern for later modification of tex file
        print("aa-bb " + "**" + funchd + "**", file=self.rf1)
        print(' ', file=self.rf1)

        # draw horizontal line
        print(".. raw:: latex", file=self.rf1)
        print('  ', file=self.rf1)
        print('   \\vspace{-1mm}', file=self.rf1)
        print('  ', file=self.rf1)
        print('   \\hrulefill', file=self.rf1)
        print('  ', file=self.rf1)

        # convert symbols to numbers - retain units
        for k1 in self.odict:
            if k1[0] != '_':
                try:
                    exec(self.odict[k1][1].strip())
                except:
                    pass
            if k1[0:2] == '_a':
                #print('ek1-2', k1)
                try:
                    exec(self.odict[k1][3].strip())
                    exec(self.odict[k1][4].strip())
                    exec(self.odict[k1][1].strip())
                except:
                    pass

        # evaluate function
        print(" ", file=self.rf1)
        print('return variable: ' + dval[2].strip(), file=self.rf1)
        print(" ", file=self.rf1)
        print('function call: ' + dval[1].strip(), file=self.rf1)
        funcname = dval[1].split('(')[0]
        docs1 = eval(funcname + '.__doc__')
        print('  ', file=self.rf1)
        print('**function doc string:**', file=self.rf1)
        print('  ', file=self.rf1)
        print('::', file=self.rf1)
        print('  ', file=self.rf1)
        print('  ' + docs1, file=self.rf1)
        print('  ', file=self.rf1)

        return1 = eval(dval[1].strip())
        if return1 is None:
            print('function evaluates to None', file=self.rf1)
            print('  ', file=self.rf1)
        else:
            print('**function returned:** ', file=self.rf1)
            tmp1 = str(return1)
            if '[[' in tmp1:
                tmp2 = tmp1.replace(' [', '.  [')
                tmp1 = tmp2.replace('[[', '. [[')
            elif '[' in tmp1:
                tmp1 = tmp1.replace('[', '. [')
            else:
                if tmp1[0:2] != '  ':
                    tmp1 = '  ' + tmp1
            print('  ', file=self.rf1)
            print('::', file=self.rf1)
            print('  ', file=self.rf1)
            print(tmp1, file=self.rf1)
            print('  ', file=self.rf1)
            print(".. raw:: latex", file=self.rf1)
            print('  ', file=self.rf1)
            print('   \\vspace{2mm}', file=self.rf1)
            print('  ', file=self.rf1)

    def _rst_eq(self, var3, dval):
        """print equation

        equations dict:
        [[e], statement, expr, ref, decimals, units, prnt opt]
        key = var3

        """
        try:
            eformat, rformat = dval[4].split(',')
            exec("set_printoptions(precision=" + eformat + ")")
            exec("Unum.VALUE_FORMAT = '%." + eformat + "f'")
        except:
            eformat = '3'
            rformat = '3'
            set_printoptions(precision=3)
            Unum.VALUE_FORMAT = "%.3f"

        # default print expansion
        if dval[6].strip() == '':
            dval[6] = '3'
        cunit = dval[5].strip()
        #var3 = dval[1].split("=")[0].strip()
        #val3 = eval(dval[2])

        # evaluate variables
        for k1 in self.odict:
            #print('k1', k1)
            if k1[0] != '_':
                    try:
                        exec(self.odict[k1][1].strip())
                    except:
                        pass
            if k1[0:2] == '_a':
                #print('k1-2', k1)
                try:
                    exec(self.odict[k1][3].strip())
                    exec(self.odict[k1][4].strip())
                    exec(self.odict[k1][1].strip())
                except:
                    pass

        exec(dval[1])
        # evaluate only
        if dval[6].strip() == '0':
            print('  ', file=self.rf1)
            return

        # equation reference line
        strend = dval[3].strip()
        print('  ', file=self.rf1)
        print("aa-bb " + "**" + var3 + " | " + strend + "**",
              file=self.rf1)
        print('  ', file=self.rf1)
        # draw horizontal line
        print(".. raw:: latex", file=self.rf1)
        print('  ', file=self.rf1)
        print('   \\vspace{-1mm}', file=self.rf1)
        print('  ', file=self.rf1)
        print('   \\hrulefill', file=self.rf1)
        print('  ', file=self.rf1)

        # symbolic and substituted forms
        if dval[6].strip() == '2' or dval[6].strip() == '3':
            # print symbolic form
            for _j in self.symb:
                if str(_j)[0] != '_':
                    varsym(str(_j))
            #print('dval2', dval[2])
            try:
                symeq = sympify(dval[2].strip())
                print('  ', file=self.rf1)
                print(".. raw:: latex", file=self.rf1)
                print('  ', file=self.rf1)
                print('   \\vspace{1mm}', file=self.rf1)
                print('  ', file=self.rf1)
                print('.. math:: ', file=self.rf1)
                print('  ', file=self.rf1)
                print('  ' + latex(symeq, mul_symbol="dot"), file=self.rf1)
                print('  ', file=self.rf1)
                print(".. raw:: latex", file=self.rf1)
                print('  ', file=self.rf1)
                print('   \\vspace{1mm}', file=self.rf1)
                print('  ', file=self.rf1)
            except:
                symeq = dval[2].strip()
                print('  ', file=self.rf1)
                print('::', file=self.rf1)
                print('  ', file=self.rf1)
                print('  ' + symeq, file=self.rf1)
                print('  ', file=self.rf1)

            # substitute values for variables
            if dval[6].strip() == '3':
                # list of symbols
                symat = symeq.atoms(Symbol)
                latexrep = latex(symeq, mul_symbol="dot")
                #print('latex', latexrep)
                switch1 = []
                # rewrite latex equation withbraces
                for _n in symat:
                    newlatex1 = str(_n).split('__')
                    if len(newlatex1) == 2:
                        newlatex1[1] += '}'
                        newlatex1 = '~d~'.join(newlatex1)
                    newlatex1 = str(_n).split('_')
                    if len(newlatex1) == 2:
                        newlatex1[1] += '}'
                        newlatex1 = '~s~'.join(newlatex1)
                    newlatex1 = ''.join(newlatex1)
                    newlatex1 = newlatex1.replace('~d~', '__{')
                    newlatex1 = newlatex1.replace('~s~', '_{')
                    #symeq1 = symeq1.subs(_n, symbols(newlatex1))
                    switch1.append([str(_n), newlatex1])
                # substitute values
                for _n in switch1:
                    #print('swi', (self.odict[_n[0]][1]).split("=")[1])
                    # avoid problems with units
                    try:
                        expr1 = eval((self.odict[_n[0]][1]).split("=")[1])
                        if type(expr1) == float:
                            form = '{:.' + eformat.strip() +'f}'
                            symvar1 = '{' + form.format(expr1) + '}'
                        else:
                            symvar1 = '{' + str(expr1) + '}'
                        #print('replace',_n[1], symvar1)
                        latexrep = latexrep.replace(_n[1], symvar1)
                        latexrep = latexrep.replace("\{", "{")
                        #print(latexrep)
                    except:
                        pass
                # add substituted equation to rst file
                print('  ', file=self.rf1)
                print('.. math:: ', file=self.rf1)
                print('  ', file=self.rf1)
                print('  ' + latexrep, file=self.rf1)
                print('  ', file=self.rf1)
                print(".. raw:: latex", file=self.rf1)
                print('  ', file=self.rf1)
                print('   \\vspace{1mm}', file=self.rf1)
                print('  ', file=self.rf1)
                print('  ', file=self.rf1)
            # restore units
            for j2 in self.odict:
                try:
                    state = self.odict[j2][1].strip()
                    exec(state)
                except:
                    pass

        #convert result variable to greek
        var3s = var3.split('_')
        if var3s[0] in greeks:
            var3g = "\\" + var3
        else:
            var3g = var3
        # print result
        typev = type(eval(var3))
        #print('typev', typev)
        print1 = 0
        if typev == ndarray:
            print1 = 1
            tmp1 = str(eval(var3))
            if '[[' in tmp1:
                tmp2 = tmp1.replace(' [', '.  [')
                tmp1 = tmp2.replace('[[', '. [[')
            else:
                tmp1 = tmp1.replace('[', '. [')
        elif typev == list or typev == tuple:
            print1 = 1
            tmp1 = str(eval(var3))
            if '[[' in tmp1:
                tmp2 = tmp1.replace(' [', '.  [')
                tmp1 = tmp2.replace('[[', '. [[')
                tmp1 = tmp1.replace('],', '],\n')
            else:
                tmp1 = tmp1.replace('[', '. [')
                tmp1 = tmp1.replace('],', '],\n')
        elif typev == Unum:
            print1 = 2
            exec("Unum.VALUE_FORMAT = '%." + rformat.strip() + "f'")
            if len(cunit) > 0:
                tmp = eval(var3).asUnit(eval(cunit))
            else:
                tmp = eval(var3)
            tmp1 = tmp.strUnit()
            tmp2 = tmp.asNumber()
            chkunit = str(tmp).split()
            #print('chkunit', tmp, chkunit)
            if len(chkunit) < 2:
                tmp1 = ''
            resultform = "%."+rformat + "f"
            result1 = locale.format(resultform , tmp2, grouping=True)
            tmp3 = result1 + ' '  + tmp1
        else:
            print1 = 2
            if type(eval(var3)) == float or type(eval(var3)) == float64:
                resultform = "%."+rformat + "f"
                tmp3 = locale.format(resultform , eval(var3), grouping=True)
            else:
                tmp3 = var3 +"="+ str(eval(var3))

        # for lists and arrays
        if print1 == 1:
            print('  ', file=self.rf1)
            print('::', file=self.rf1)
            print('  ', file=self.rf1)
            print('. ' + var3 + ' = ', file=self.rf1)
            print(tmp1, file=self.rf1)
            print('  ', file=self.rf1)
            print(".. raw:: latex", file=self.rf1)
            print('  ', file=self.rf1)
            print('   \\vspace{4mm}', file=self.rf1)
            print('  ', file=self.rf1)

        # for equations with and without units
        if print1 == 2:
            # add space between units
            try:
                result2 = latex(tmp3).split()
                tmp3 = ''.join(result2[:-2]) + ' \ '.join(result2[-2:])
            except:
                pass
            print(' ', file=self.rf1)
            print('.. math:: ', file=self.rf1)
            print('  ', file=self.rf1)
            print("  {" + latex(tmp3, mode='plain') + "}", file=self.rf1)
            print('  ', file=self.rf1)

        print(".. raw:: latex", file=self.rf1)
        print('  ', file=self.rf1)
        print('   \\vspace{-8mm}', file=self.rf1)
        print('  ', file=self.rf1)


    def _rst_file(self, refnum):
        """process file operations from file dictionary

        model dictionary:
        '_i' : [[i], ref num, description, modnum]

        File dictionary:
        file op number :[option, file path, var1, var2, var3, modnum]

         xxxxx means add notation but don't process again

        options:
        t: add text file contents to output
            No operations are processed.
        f: insert jpg, png etc, figures into calc
       xxxxxxx r: read file data into variable - processed when tagged
       xxxxxxx e: edit file. Store edits in var3. (multiline)

        For non-equation entries the dictionary key is:
        _x + incremented number - pass-through text
        _y + incremented number - symbolic representation
        _s + incremented number - sections
        _t + incremented number - inserted text
        _p + incremented number - python code
        _c + incremented number - check operation
        _a + incremented number - array and ranges
        _m + incremented number - current model directory
        _i + incremented number - file operation
        _f + incremented number - function
        _pd - license text

        """
        dval = self.fidict[refnum[1]]
        prt_log = self.ew.errwrite

        option = dval[0].strip()
        fpath = dval[1].strip()
        fp = os.path.abspath(fpath)
        var1 = dval[3].strip()
        var2 = dval[3].strip()
        var3 = dval[4]  # variable with edit lines

        # additional disk operation output for PDF calcs

        if option == 's':
            # execute script in model namespace
            with open(fp, 'r') as f1:
                fr = f1.read()
            exec(fr, globals())
            self.ew.errwrite("file: " + fpath + " compiled in pdf calc", 0)

        elif option ==   't':
            # insert file from text into model, do not process
            with open(fpath, 'r') as f1:
                txstrng = f1.readlines()
            if var1.strip() != '':
                instxt = eval('txstrng[' + var1.strip() + ']')
                instxt = '  '.join(instxt)
            else:
                instxt = '  '.join(txstrng)


            print('  ', file=self.rf1)
            print('::', file=self.rf1)
            print('  ', file=self.rf1)
            print('  ' + instxt, file=self.rf1)
            print('  ', file=self.rf1)

        elif option == 'f':
            self._rst_figure(dval)

        elif option == 'r':
            self._rst_read(dval)

        elif option == 'e':
            self._rst_edit(dval)

    def _rst_figure(self, dval):
        """print figure

        Dictionary Value:
        equation:[[d], optins, file path, var1, var2, var3]

        Args: str
            dval[0] - option -> 'f'
            dval[1] - data file
            var1 = dval[2] - caption
            var2 = dval[3] - percent width
            var3 = dval[4] - 'double' -> side by side figures
        """
        option = dval[0].strip()
        fpath = dval[1].strip()
        fp = os.path.abspath(fpath)
        var1 = dval[2].strip()
        var2 = dval[3].strip()

        if option == 'f':
            print(' ', file=self.rf1)
            print('.. figure:: ' + fp, file=self.rf1)
            print('   :width: ' + var2 + ' %', file=self.rf1)
            print('   :align: center', file=self.rf1)
            print('   ', file=self.rf1)
            print('   ' + var1, file=self.rf1)
            print(' ', file=self.rf1)

    def _rst_read(self, dval):
            """read csv data file

            Args: strng
            option = dval[0].strip()
            fpath = dval[1].strip()
                fp = os.path.abspath(fpath)
            var1 = dval[2].strip() # variable
            var2 = dval[3].strip() # sep character
            var3 = dval[4]  # skip lines
            var4 = data from genfromtext

            """

            option = dval[0].strip()
            fpath = dval[1].strip()
            fp = os.path.abspath(fpath)
            var1 = dval[2].strip()
            var2 = dval[3].strip()
            var3 = dval[4]

            secthead =  var1 + " | read data"

            print("aa-bb " + "**" + secthead + "**", file=self.rf1)
            print('  ', file=self.rf1)

            # set skip lines
            skip1 = dval[4]
            if skip1 == '':
                skip1 = int(0)
            else:
                skip1 = int(skip1)

            # set separator
            sep1 = var2
            if sep1 == '*':
                var4 = genfromtxt(fpath, delimiter=' ',
                                  skip_header=skip1)
            elif sep1 == ',' or sep1 == '':
                var4 = genfromtxt(fpath, delimiter=',',
                                  skip_header=skip1)
            else:
                var4 = genfromtxt(fpath, delimiter=str(sep1),
                                  skip_header=skip1)
            #print('var4', var4[:2])

            cmdstr1 = str(dval[2].strip())
            cmdstr2 = cmdstr1 + '=' + str(list(var4))
            self.odict[cmdstr1] = ['[rd]', cmdstr2]
            #print(self.odict[cmdstr1])

            # print data selection
            print('  ', file=self.rf1)
            print("file: " + dval[1].strip(), file=self.rf1)
            print('  ', file=self.rf1)
            print(str(var4[:4]) + ' ... ' + str(var4[-4:]),
                  file=self.rf1)
            print('  ', file=self.rf1)


            # draw line
            print(".. raw:: latex", file=self.rf1)
            print('  ', file=self.rf1)
            print('   \\hrulefill', file=self.rf1)
            print('  ', file=self.rf1)
            print(".. raw:: latex", file=self.rf1)
            print('  ', file=self.rf1)
            print('   \\vspace{2mm}', file=self.rf1)
            print('  ', file=self.rf1)

            #print('mdict', self.mdict[str(var1)])

    def _rst_edit(self, dval):
        """ write edit option to rst file

        Args: str
            option = dval[0].strip()
            fpath = dval[1].strip()
            fp = os.path.abspath(fpath)
            var1 = dval[2].strip()
            var2 = dval[3].strip()
            var3 = dval[4]  # variable with edit lines
        """
        editlist = []
        var3 = dval[0]

        for item in var3:
            editlist.append(item)

        strend = dval[1].strip() + " | edit file"
        print("aa-bb " + "**" + strend + "**",
              file=self.rf1)
        print(" ", file=self.rf1)

        # draw line
        print(".. raw:: latex", file=self.rf1)
        print('  ', file=self.rf1)
        print('   \\hrulefill', file=self.rf1)
        print('  ', file=self.rf1)
        print(".. raw:: latex", file=self.rf1)
        print('  ', file=self.rf1)
        print('   \\vspace{2mm}', file=self.rf1)
        print('  ', file=self.rf1)

        # edit table
        print('  ', file=self.rf1)
        print('::', file=self.rf1)
        print('  ', file=self.rf1)
        print("  file: " + dval[1].strip(), file=self.rf1)
        title1 = '  [line #]'.center(8) + \
                 '[replacement line]'.rjust(25)
        print(title1, file=self.rf1)
        for _i in editlist[:-1]:
            _j = _i.split('|')
            print(('     ' + _j[0].strip()).ljust(10)
                          + (_j[1].strip()), file=self.rf1)
        print(' ', file=self.rf1)

    def _rst_txt(self, txt):
        """output pass-through text"""
        if txt[1].strip()[0] != '#':
            print(txt[1].strip(), file=self.rf1)

    def _rst_blnk(self):
        """print blank line"""
        print('  ', file=self.rf1)
        print(".. raw:: latex", file=self.rf1)
        print('  ', file=self.rf1)
        print('   \\vspace{4mm}', file=self.rf1)
        print('  ', file=self.rf1)