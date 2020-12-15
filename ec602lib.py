"""tools for analyzing and checking C++ and Py programs"""
import subprocess as sub
import difflib
import unittest
import re
import tokenize
import dis
import io
import cpplint
import sys
import pycodestyle
import logging
import os
import random
import importlib
import multiprocessing
from io import StringIO
import time

from subprocess import PIPE,Popen,run,TimeoutExpired

DEBUG = False

#
#
#
# 2.9 fixed overallpy
# 3.0 fixed progname / realfilename problem
# 3.1 no bracket check on smallest_largest
# 3.3 added compile_main function
# 3.4 improved code metrics cpp
# 3.5 changed test letters to allow words
# 3.6 add timeout
# 3.7 allow testorder other than alpha
# 3.8 print checker version
# 3.9 check for windows CRLF in author list
# 4.1 check the path of user for .
# 4.2 better messaging with file not founds.
# 4.3 quit if path not correct
# 4.4 add compile_separate function
# 4.5 change style to style. from 3.

VERSION = (4, 5)

path = os.environ['PATH']

if path.startswith(".:") or path.endswith(":.") or ":.:" in path:
    pass # path ok
else:
    print("""Your path is not set correctly. The checker will not work
unless you add "." the current working directory to your PATH.

You can do this by editing ~/.zshrc
""",file=sys.stderr)
    sys.exit(42)

class TimeoutException(Exception):
    pass


class RunableProcessing(multiprocessing.Process):
    def __init__(self, func, *args, **kwargs):
        self.queue = multiprocessing.Queue(maxsize=1)
        args = (func,) + args
        multiprocessing.Process.__init__(self, target=self.run_func, args=args, kwargs=kwargs)

    def run_func(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            self.queue.put((True, result))
        except Exception as e:
            self.queue.put((False, e))

    def done(self):
        return self.queue.full()

    def result(self):
        return self.queue.get()


def timeout(seconds, force_kill=True):
    def wrapper(function):
        def inner(*args, **kwargs):
            now = time.time()
            proc = RunableProcessing(function, *args, **kwargs)
            proc.start()
            proc.join(seconds)
            if proc.is_alive():
                if force_kill:
                    proc.terminate()
                runtime = int(time.time() - now)
                raise TimeoutException('timed out after {0} seconds'.format(runtime))
            assert proc.done()
            success, result = proc.result()
            if success:
                return result
            else:
                raise result
        return inner
    return wrapper


STDLINT = ['-readability/alt_tokens',"+build/include_alpha"]

ignore_lint = [x[1:] for x in STDLINT if x.startswith('-')]

ASTYLE_OPTIONS = [
    '--style=google', '--indent=spaces=2', '--formatted', '--dry-run'
]

COMMENT_STRING = {'py': '#', 'sh': "#", 'cpp': '//'}

#CPP_CODE_ONLY = [
#    'g++', '-std=c++14', '-P', '-x', 'c++', '-dD', '-E', '-fpreprocessed'
#]
def silent_import(fname, q):

    s = StringIO()
    sys.stdout = s

    themod = None
    try:
        themod = importlib.import_module(fname)
    except Exception as e:
        q.put("fail")
        return
    q.put("success")

def my_import(modname, code):
    filename = modname+".py"
    with open(filename,'w') as f:
        f.write(code)

    q = multiprocessing.Queue()

    T = multiprocessing.Process(target=silent_import,args=(modname, q))
    T.start()
    try:
        result = q.get(True,1) 
    except Exception as e:
        repeat_terminate(T,0.1)
        return False

    if result=="success":
        return importlib.import_module(modname)
    return False


def safe_remove(filename):
    try:
        os.remove(filename)
    except Exception as e:
        print(e)

def numbers_only(word_lines):
    rr=[]
    for v in word_lines:
        g=v.split()
        nums=[]
        for x in g:
            try:
                nums.append(int(x))
            except:
                try:
                    nums.append(float(x))
                except:
                    pass
        rr.append(nums)

    return rr

bracket_msg="""You are not allowed to use brackets []

a) Use .at() or other methods instead
b) replace c-style arrays with vectors or strings etc
c) if you must use a c-style array (e.g. argv) use pointers

You have {} brackets.
"""

report_msg="""
===============================
Checking {prog} for EC602 submission
{version}
================================

Information
-----------
{info}

Passed Tests
------------
{passed}

Failed Tests
------------
{failed}

Grading
-------
{grade}"""

AUTHWARN = "WARNING, NO VALID AUTHOR LINES FOUND"

def setup_py(cls, prefix):
    with open(cls.realfilename) as f:
        cls.file_contents=f.read()

    cls.module_name = prefix+str(random.randint(1000,100000))

    cls.module_tested = my_import(cls.module_name, cls.file_contents)
    if not cls.module_tested:
      safe_remove(cls.module_name+".py")
      raise unittest.SkipTest(f'During test of {cls.__doc__}, unable to import your module. Timeout or error')




def compile_main(cls,prefix):
        if not hasattr(cls,'lintoptions'):
            cls.lintoptions = STDLINT

        try:
            with open(cls.realfilename) as f:
              cls.file_contents=f.read()
        except:
            raise unittest.SkipTest(f"in compile_main, {cls.realfilename} not found.")

        cls.executable = prefix+str(random.randint(1000,100000))
        cls.new_source_file_main = cls.executable + ".cpp"
    
        with open(cls.new_source_file_main,'w') as f:
            f.write(cls.file_contents_main)

        try:
            T = sub.run(["g++","-std=c++17",'-Wall','-Wno-sign-compare',
                         cls.new_source_file_main,"-o",cls.executable],
             stderr=sub.PIPE,universal_newlines=True)
        except Exception as e:
          raise unittest.SkipTest("Compile failed.\n"+str(e))
        finally:
          os.remove(cls.new_source_file_main)
        cls.code_metrics = code_analysis_cpp(cls.realfilename,cls.lintoptions)



def compile_separate(cls,prefix):
        if not hasattr(cls,'lintoptions'):
            cls.lintoptions = STDLINT

        try:
            with open(cls.realfilename) as f:
              cls.file_contents=f.read()
        except:
            raise unittest.SkipTest(f"in compile_separate, {cls.realfilename} not found.")

        cls.executable = prefix+str(random.randint(1000,100000))
        cls.new_source_file_main = cls.executable + ".cpp"
    
        with open(cls.new_source_file_main,'w') as f:
            f.write(cls.file_contents_main)

        try:
            T = sub.run(["g++","-std=c++17",'-Wall','-Wno-sign-compare',
                         cls.realfilename,cls.new_source_file_main,"-o",cls.executable],
             stderr=sub.PIPE,universal_newlines=True)
        except Exception as e:
          raise unittest.SkipTest("Compile failed.\n"+str(e))
        finally:
          os.remove(cls.new_source_file_main)
        cls.code_metrics = code_analysis_cpp(cls.realfilename,cls.lintoptions)



def compile(self,prefix):
        if not hasattr(self,'lintoptions'):
            self.lintoptions = STDLINT

        try:
            with open(self.realfilename) as f:
              self.file_contents=f.read()
        except:
            raise unittest.SkipTest(f"in compile, {self.realfilename} not found.")

        self.executable = prefix+str(random.randint(1000,100000))
        new_source_file = self.executable + ".cpp"
    
        with open(new_source_file,'w') as f:
            f.write(self.file_contents)

        try:
            T = sub.run(["g++","-std=c++17",'-Wall','-Wno-sign-compare',new_source_file,"-o",self.executable],
             stderr=sub.PIPE,universal_newlines=True)
        except Exception as e:
          raise unittest.SkipTest("Compile failed.\n"+str(e))
        finally:
            os.remove(new_source_file)
        self.code_metrics = code_analysis_cpp(self.realfilename,self.lintoptions)




def compile_and_run(self,prefix):
        compile(self,prefix)
        try:
          T = sub.run([self.executable],stdout=sub.PIPE,stderr=sub.PIPE,timeout=1,universal_newlines=True)
        except Exception as e:
           safe_remove(self.executable)
           raise unittest.SkipTest("Failed to run.\n"+str(e))
        self.output = T.stdout
        self.errors = T.stderr



def bracket_check(self):
    "brackets. check for brackets"
    bracket_count =  self.code_metrics['brackets']
    if bracket_count:
      self.fail(bracket_msg.format(bracket_count))



def test_includes(self):
    "includes. check the included libraries are allowed"

    includes = get_includes(self.file_contents)
    self.msgs.append('included libraries : {}\n'.format(" ".join(includes) if includes else "None"))

    if self.valid_includes=="Any":
        return

    invalid_includes = includes - self.valid_includes
    if invalid_includes:
        self.fail('Invalid includes: {}'.format(" ".join(x for x in invalid_includes)))

def test_imports(self):
    "imports. check the imported modules are allowed"

    includes = get_python_imports(self.file_contents)
    self.msgs.append('imported modules : {}\n'.format(" ".join(includes) if includes else "None"))

    invalid_includes = includes - self.valid_includes
    if invalid_includes:
        self.fail('Invalid imports: {}'.format(" ".join(x for x in invalid_includes)))



def test_authors(self):
    "authors. check on authors' emails identified"

    authors = get_authors(self.file_contents, progtype(self.realfilename))

    self.msgs.append('authors          : {}\n'.format(" ".join(authors)
                                               if authors else AUTHWARN))

    if len(authors)==0:
        self.fail('No authors found in your document.')
    elif len(authors) > self.authorlimit:
        self.fail('Author limit {self.authorlimit} exceeded.')


def test_pystyle(self):
    "style. python code style and analysis"
    proc_pycodestyle = sub.run(['pycodestyle', self.realfilename], stdout=sub.PIPE)

    prob = False
    if proc_pycodestyle.returncode:
        prob = proc_pycodestyle.stdout.decode().rsplit(" ", 1)[-1].strip()

    self.msgs.append("pycodestyle check: {}\n".format("{} problems".format(
        len(proc_pycodestyle.stdout.decode().splitlines())) if prob else "ok"))

    proc_pylint = sub.run(
        ['pylint', self.realfilename], stdout=sub.PIPE,stderr=sub.PIPE)

    pylint_report = proc_pylint.stdout.decode().splitlines()
    if len(pylint_report)<2:
        logging.error('bad pylint_report'+proc_pylint.stdout.decode())
        pylint_score = 0
    elif "previous" in pylint_report[-2]:
        pylint_score=pylint_report[-2].split()[6]
    else:
        pylint_score = pylint_report[-2].split()[-1]
        
    self.msgs.append("pylint score     : {}\n".format(pylint_score))
 
    code_metrics = code_analysis_py(self.file_contents)
    self.msgs.append(code_size_report(code_metrics, self.refcode))
    comments = 0
    for line in self.file_contents.splitlines():
        if '#' in line:
            comments += 1

    self.msgs.append("comments         : {}\n".format(comments))


def test_cppstyle(self):
    "style. C++ code style and analysis"

    comments = 0
    for line in self.file_contents.splitlines():
        if '//' in line:
            comments += 1


 
    cm = self.code_metrics
    if cm['errors']:
        numerrors=sum(len(x) for x in cm['errors'].values())

        self.msgs.append(f"cpplint       : {numerrors} problems")
        cpplint_call_list = [
            'cpplint', '--filter=' + ','.join(self.lintoptions), self.__doc__
        ]

        self.msgs.append('  [using {}]\n\n'.format(' '.join(cpplint_call_list)))

        for e in cm['errors']:
            for x in cm['errors'][e]:
                    self.msgs.append('  line {} ({}): {}'.format(*x))
    else:
        self.msgs.append("cpplint       : ok")

    
    self.msgs.append(f"astyle        : {cm['astyle']:.1%} code unchanged.")

    self.msgs.append(code_size_report(cm, self.refcode))

    self.msgs.append(f"comments      : {comments}")



def read_file(filename):
    "read the contents of filename into string"
    filehand = open(filename)
    contents = filehand.read()
    filehand.close()
    return contents

def read_file_for_cpplint(filename):
    "read the contents of filename into list of strings"
    filehand = open(filename)
    contents = filehand.read()
    filehand.close()
    lines = contents.splitlines()
    if contents.endswith('\n'):
        lines.append('')
    return lines


def make_grades(gradesummary,Penalty,Points,special_str="",spec_grade=0):
    grade = 0
    grade_report = special_str

    grade_report += "Points for passed tests:\n"
    for test in sorted(Points):
        if test in gradesummary['pass']:
            if Points[test]==int(Points[test]):
                grade_report += f" {test}({Points[test]})\n"
            else:
                grade_report += f" {test}({Points[test]:.2f})\n"
            grade += Points[test]
    grade_report += "\n"

    for test in Penalty:
        if test in gradesummary['fail']:
            grade_report += "Penalty for failed test {}: {}\n".format(test,Penalty[test])
            grade -= Penalty[test]
   
    grade = max(grade+spec_grade,0)
    grade_report += "\nGrade: {}".format(grade)

    return grade, grade_report


def code_analysis_cpp(program_filename,lintoptions):
    ignore_lint = [x[1:] for x in lintoptions if x.startswith('-')]
    Errors = {}
    def error_fcn(filename,line_number,lint_type,level,message):
        category,subcategory = lint_type.split('/')
        if category not in Errors:
            Errors[category]=[]
        Errors[category].append( (line_number,lint_type,message) )

    lines = read_file_for_cpplint(program_filename)
    cpplint.RemoveMultiLineComments(program_filename,lines,error_fcn)

    clean_lines = cpplint.CleansedLines(lines)

    cpplint.ProcessFileData(program_filename,'cpp',lines,error_fcn)

    the_lines = [x for x in clean_lines.lines if x]
    num_lines=len(the_lines)
    num_words = sum(len(x.split()) for x in the_lines)

    num_brackets = sum(x.count('[') for x in the_lines)
    

    original = read_file(program_filename)
    proc_astyle = sub.run(
        ['astyle', *ASTYLE_OPTIONS],
        input=original.encode(),
        stdout=sub.PIPE,
        stderr=sub.PIPE)

    if proc_astyle.returncode:
        unchanged='error'
    else:
        original = original.splitlines()
        newprog = proc_astyle.stdout.decode().splitlines()
        matcher = difflib.SequenceMatcher()
        matcher.set_seqs(original, newprog)
        unchanged = matcher.ratio()

    RealErrors={}

    for e in Errors:
        RealErrors[e]=[]
        for x in Errors[e][:3]:
            ignore=False
            for s in ignore_lint:
              if x[1] in s:
                ignore=True;
            if not ignore:
                RealErrors[e].append(x)

    return {'brackets':num_brackets,
            'lines': num_lines,
            'words': num_words,
            'errors':RealErrors,
            'astyle':unchanged}


def isstring(x):
    x=x.strip()
    if not x:
        return True
    elif x.startswith('#'):
        return True
    elif x.startswith('"""') and x.endswith('"""'):
        return True
    elif x.startswith("'''") and x.endswith("'''"):
        return True
    elif x.startswith('"') and x.endswith('"'):
        return True
    elif x.startswith("'") and x.endswith("'"):
        return True

def code_analysis_py(program_contents):
        "count lines and words in python"
        # remove docstrings
        for search_str in ('\"\"\"[^\"]*\"\"\"',"\'\'\'[^\']*\'\'\'"):
            for x in re.findall(search_str,program_contents,flags=re.MULTILINE|re.DOTALL):
                program_contents = program_contents.replace(x,'')


        srclines=program_contents.splitlines()

        # remove single line strings.
        srclines = [x for x in program_contents.splitlines() if not isstring(x)]

        src ="\n".join(srclines)
        #print(src)
        return {'lines': len(src.splitlines()), 'words': len(src.split())}

pylint_options=["--enable=all","--reports=yes","--persistent=no",
"--msg-template='{category:10s}:{line:3d},{column:2d}: {msg} ({symbol})'"]

def pylint_check(program_name):
    process = sub.run(['pylint',program_name,*pylint_options],
        stdout=sub.PIPE,universal_newlines=True)
    
    out_str = process.stdout
    for scoreline in out_str.splitlines()[-4:]:
        try:
            score = float(re.search('Your code has been rated at ([\d|\.]*)/10',scoreline).groups()[0])
            return score, out_str
        except:
            pass
    raise ValueError('could not get your pylint score')


def pycodestyle_check(filename):
    "run pycodestyle, return #errors and error string"

    pycodestyle_res = io.StringIO()

    sys.stdout = pycodestyle_res
    pycodestyle_errors = pycodestyle.Checker(filename).check_all()
    sys.stdout = sys.__stdout__

    res = pycodestyle_res.getvalue()


    return pycodestyle_errors,res


def progtype(program):
    "which type, cpp or py"
    _, program_type = program.split('.')
    return program_type


def get_includes(file_contents):
    "get included libraries in C/C++"
    includes = set()
    for line in file_contents.lower().splitlines():
        text = line.strip()
        search_str = r"#include\s*<(.*)>"
        matches = re.match(search_str, text)
        if matches:
            includes.add(matches.group(1))
        matches = re.match("#include \"(.*)\"", text)
        if matches:
            includes.add(matches.group(1))
    return includes


def get_python_imports(file_contents):
    "get the imports of file_contents as a set"
    try:
        instructions = dis.get_instructions(file_contents)
        imports = [__ for __ in instructions if 'IMPORT' in __.opname]
    except:
        return {'ERROR PROCESSING PYTHON SCRIPT'}

    grouped = set()
    for instr in imports:
        if instr.opname == "IMPORT_NAME":
            grouped.add(instr.argval)

    return grouped




def get_authors(file_contents, ptype):
    """get the authors in file_contents"""
    authors = []
    if ptype == 'json':
        A = json.loads(file_contents)
        return A.get('authors',[])

    for line in file_contents.lower().splitlines():
        if line.startswith(COMMENT_STRING[ptype]) and "copyright" in line:
            try:
                _, email = line.strip().rsplit(" ", 1)
                if email.endswith('@bu.edu'):
                    authors.append(email)
                elif email.endswith('\r'):
                    authors.append('DONT_USE_WINDOWS_ENDLINES')
            except:
                pass
    return authors


def check_program(testclass,testorder=None,versioninfo=None,theprog=None):
    """return any errors as a list of strings"""

    errors = []
    passed = []
    gradesummary = {'pass': [], 'fail': []}
    testclass.realfilename = theprog

    if hasattr(testclass, "setUpClass"):
        try:
            testclass.setUpClass()
        except Exception as e:
            return f"{testclass} setup fail {e}",0


    loader = unittest.loader.TestLoader()
    tests = loader.loadTestsFromTestCase(testclass)
    def f(test,order):
        testname=test.shortDescription().split('.')[0]
        i = testorder.index(testname)
        return i
    if testorder:
        alltests = sorted(tests,key=lambda x: f(x,testorder) )
    else:
        alltests = sorted(tests, key=lambda x: x.shortDescription())
    for test in alltests:
        if DEBUG: print('running test:' ,test.shortDescription())
        run = test.run()

        if run.wasSuccessful():
            passed.append('{}\n'.format(test.shortDescription()))
            gradesummary['pass'].append(test.shortDescription().split('.')[0])
        else:
            err = '{}\n'.format(test.shortDescription())
            for testmsg, res in run.failures + run.errors:
                casetext = re.search(".*CASE='(.*)'", str(testmsg))
                if casetext:
                    err += "CASE: {}\n".format(casetext.group(1))
                if 'AssertionError:' in res:
                    _, msg = res.split('AssertionError: ')
                else:
                    msg = res
                err += msg
            errors.append(err)
            gradesummary['fail'].append(test.shortDescription().split('.')[0])

    if hasattr(testclass, "tearDownClass"):
        testclass.tearDownClass()
    grade, grade_report = make_grades(gradesummary,testclass.Penalty,testclass.Points)
    msg = report_msg.format(info="\n".join(testclass.msgs),
         passed=''.join(passed) if passed else "None",
         failed=''.join(errors) if errors else "None",
         grade = grade_report,
         prog = testclass.__doc__,
         version = versioninfo or "")

    return msg, grade


EMPTYGRADE = {'pass': [], 'fail': []}


def errors_msg(errors):
    "format error message"
    msg = '-----------------errors found--------------\n'
    for testmsg in errors:
        msg += testmsg + "\n-------\n"
    return msg


SIZE_REPORT_TEMPLATE = """lines of code    : {}, {:4.0%} of reference
tokens in code   : {}, {:4.0%} of reference
"""


def code_size_report(submitted_code, reference_code):
    "generate message about code size"
    return SIZE_REPORT_TEMPLATE.format(
        submitted_code['lines'],
        submitted_code['lines'] / reference_code['lines'],
        submitted_code['words'],
        submitted_code['words'] / reference_code['words'])


def pyshell(Parms,q):
      summary, results, gradesummary = overallpy(**Parms)    
      q.put([summary,results,gradesummary])

def check_program_shell(Parms,q):
    q.put(check_program(**Parms))

