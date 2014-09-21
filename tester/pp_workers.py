def gen_test (testname, generator, gen_params):
  open(testname+".in", "w").write(generator(*gen_params))
  return testname

def gen_correct (testname, correct_prog):
  import subprocess32
  subprocess32.call(
                  ("./"+correct_prog,),
                  stdin=open(testname+".in", "r"),
                  stdout=open(testname+".out", "w"),
                  )
  return testname

def test_case (testname, timeout, prog_name, checker):
  import subprocess32
  try:
    q=subprocess32.call(
                          ("./"+prog_name,),
                          stdin=open(testname+".in", "r"),
                          stdout=open(testname+".test", "w"),
                          timeout=timeout
                        )
  except:
    return (testname, 2)
  if q!=0:
    return (testname, "program returned code {}.".format(q))
  if checker=="diff":
    return (
            testname,
            subprocess32.call(
                                ("diff", "-qb", testname+".out", testname+".test"),
                                stdout=open("/dev/null", "w")
                              )
            )
  else:
    return (
            testname,
            subprocess32.call(
                                ("./"+checker, testname+".out", testname+".test", testname+".in"),
                                stdout=open("/dev/null", "w")
                              )
            )
