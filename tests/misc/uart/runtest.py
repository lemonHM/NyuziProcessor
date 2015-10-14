#!/usr/bin/env python
# 
# Copyright 2011-2015 Jeff Bush
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 

import sys

sys.path.insert(0, '../..')
import test_harness

def test_uart(name):
	test_harness.compile_test('uart.c')
	result = test_harness.run_verilator()
	if result.find('PASS') == -1:
		raise TestException('test did not indicate pass')

test_harness.register_tests(test_uart, ['uart'])
test_harness.execute_tests()
