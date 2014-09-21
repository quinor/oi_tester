#!/usr/bin/env python2
from tester import Tester

def case (k):
	import random
	k=random.randint(1,k)
	chance=random.random()
	return str(k)+"\n"+"".join("j" if random.random()>chance else "p" for i in range(k))+"\n"

tester=Tester("bar")
tester.add_testcase(100, case, (20,), "small")
tester.add_testcase(100, case, (10**3,), "mid")
tester.add_testcase(100, case, (10**6,), "max")

tester.clean()
tester.generate_tests()
tester.generate_correct_answers()
tester.run_testing()
tester.make_package()
