import os
import pp
import glob
import threading
from pp_workers import *

class Tester (object):
  """
  OI tester class. Automatically generates tests and checks program correctness.
  """
  def __init__ (self, name, jobs_num=10, timeout=10, checker="diff", save_errors=True):
    """
    Arguments:
      name          -- name of tested program, usually 3-letter task code
      jobs_num      -- number of threads
      timeout       -- timeout for tested program
      checker       -- optional custom checker, launched: ./checker file.out file.test file.in
                       returns 0 if correct, 1 if wrong answer
      save_errors   -- determines whether wrong answer tests are saved in error folder
    """
    self.__name=name
    self.__prog_correct=self.__name+"_wzor"
    self.__path=self.__name+"_test"
    self.__jobs_num=jobs_num
    self.__timeout=timeout
    self.__checker=checker
    self.__save_errors=save_errors
    self.__error_folder=self.__name+"_error"
    self.__error_file=self.__name+".err"
    self.__cases=[]
    self.__lock=threading.Lock()
    self.__zeroes=5
    self.__server=pp.Server(self.__jobs_num)
  
  def add_testcase (self, quanity, function, params, prefix=None):
    """
    Adds testcase to Tester instance.
    Arguments:
      quanity           -- number of test cases generated with this function and params set
      function          -- function generating one test case (as string) when supplied with unpacked params
      params            -- a tuple of parameters with which function is called
      prefix (optional) -- additional specificator for this group of tests added to filenames
    """
    if prefix is not None:
      prefix="_"+prefix
    self.__cases.append((quanity, function, params, prefix))
  
  def generate_tests (self):
    """
    Generates tests basing on added testcases.
    """
    num=0
    self.__num_done=0
    self.__tests_quanity=sum(e[0] for e in self.__cases)
    os.system("mkdir {}".format(self.__path))
    filename=self.__path+"/"+self.__name+"{}{}"
    for quanity, func, params, prefix in self.__cases:
      for i in range(quanity):
        self.__server.submit(
                              gen_test,
                              (
                                filename.format(prefix, num),
                                func,
                                params
                              ),
                              callback=self.__test_generated
                            )
        num+=1
    self.__server.wait()
  
  def __test_generated (self, filename):
    self.__lock.acquire()
    self.__num_done+=1
    print ("\033[1;33mTEST GENERATED\033[0m "+self.__done_info(self.__num_done, self.__tests_quanity)+" "+filename)
    self.__lock.release()
  
  def generate_correct_answers (self):
    """
    Generates correct answers for existing tests.
    """
    testfiles=[x[:-3] for x in glob.glob(self.__path+"/*.in")]
    self.__num_done=0
    self.__tests_quanity=len(testfiles)
    for filename in testfiles:
      self.__server.submit(
                            gen_correct,
                            (
                              filename,
                              self.__prog_correct
                            ),
                            callback=self.__answer_generated
                          )
    self.__server.wait()
  
  def __answer_generated (self, filename):
    self.__lock.acquire()
    self.__num_done+=1
    print ("\033[1;33mANSWER GENERATED\033[0m "+self.__done_info(self.__num_done, self.__tests_quanity)+" "+filename)
    self.__lock.release()

  def run_testing (self):
    """
    Tests program on every existing test.
    """
    self.__error_file_object=open(self.__error_file, "w")
    if self.__save_errors:
      os.system("mkdir {}".format(self.__error_folder))
    testfiles=[x[:-3] for x in glob.glob(self.__path+"/*.in")]
    self.__correct=0
    self.__num_done=0
    self.__tests_quanity=len(testfiles)
    for filename in testfiles:
      self.__server.submit(
                            test_case,
                            (
                              filename,
                              self.__timeout,
                              self.__name,
                              self.__checker,
                            ),
                            callback=self.__tested
                          )
    self.__server.wait()
    print self.__done_info(self.__correct, self.__tests_quanity)+" of correct answers"
  
  def __tested (self, result):
    self.__lock.acquire()
    filename, code = result
    self.__num_done+=1
    f=self.__done_info(self.__num_done, self.__tests_quanity) + filename
    if code == 0:
      print "\033[1;32mOK\033[0m        " + f
      self.__correct+=1
    elif code == 1:
      print "\033[1;31mWA\033[0m        " + f
      self.__error_file_object.write("WA  " + f+"\n")
      if self.__save_errors:
        os.system("cp {:s}.* {:s}".format(filename, self.__error_folder))
    elif code == 2:
      print "\033[1;33mTLE\033[0m       " + f
      self.__error_file_object.write("TLE " + f+"\n")
      if self.__save_errors:
        os.system("cp {:s}.* {:s}".format(filename, self.__errorfolder))
    else:
      print "\033[1;33mRE\033[0m        " + f + "(code \033[1;37m{0}\033[0m)".format(code)
    self.__lock.release()
  
  def make_package (self):
    """
    makes .tar.gz package containing all tests from testfolder
    """
    os.system("rm {}/*.test".format(self.__path))
    os.system("tar czf {}_tests.tar.gz {}".format(self.__name, self.__path))
  
  def clean (self):
    """
    removes all files created while testing
    """
    os.system("rm {} {} {} -r".format(self.__path, self.__error_folder, self.__error_file))

  def __done_info (self, first, second):
    return  "[\033[1;36m"+\
            str(first).zfill(self.__zeroes)+\
            "\033[0m/\033[1;34m"+\
            str(second).zfill(self.__zeroes)+\
            "\033[0m] "
