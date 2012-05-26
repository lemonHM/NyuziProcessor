#!/usr/bin/python
#
# Generate random instruction sequences and verify processor execution
# matches.
#

import subprocess, tempfile, os, sys, random, struct, inspect, types, re
from types import *
from generate import *
from reference import *

try:
	os.makedirs('WORK/')
except:
	pass

vectorRegPattern = re.compile('(?P<pc>[0-9a-fA-f]+) \[st (?P<strand>\d+)\] (?P<reg>v\s?\d+)\{(?P<mask>\d+)\} \<\= (?P<value>[xzXZ0-9a-fA-f]+)')
scalarRegPattern = re.compile('(?P<pc>[0-9a-fA-f]+) \[st (?P<strand>\d+)\] (?P<reg>s\s?\d+) \<\= (?P<value>[xzXZ0-9a-fA-f]+)')

class VerilogSimulatorWrapper:
	def __init__(self):
		self.INTERPRETER_PATH = 'vvp'
		self.VVP_PATH = '../../verilog/sim.vvp'
		self.MEMDUMP_FILE = 'WORK/memory.bin'

	def runTest(self, filename):
		args = [self.INTERPRETER_PATH, self.VVP_PATH, '+bin=' + filename, 
			'+regtrace=1', '+memdumpfile=' + self.MEMDUMP_FILE, '+memdumpbase=0', 
			'+memdumplen=' + str(0x10000), '+simcycles=20000' ]

		if 'VVPTRACE' in os.environ:
			args += ['+trace=trace.vcd']

		try:
			process = subprocess.Popen(args, stdout=subprocess.PIPE)
			output = process.communicate()[0]
		except:
			print 'killing simulator process'
			process.kill()
			raise

		registerTraces = [ [] for x in range(4) ]
		halted = False
		for line in output.split('\n'):
			print line
			if line.find('***HALTED***') != -1:
				halted = True

			got = vectorRegPattern.match(line)
			if got:
				registerTraces[int(got.group('strand'))] += [ (got.group('pc'), got.group('reg'), got.group('mask'), got.group('value') ) ]
			else:
				got = scalarRegPattern.match(line)
				if got:
					registerTraces[int(got.group('strand'))] += [ (got.group('pc'), got.group('reg'), got.group('value') ) ]

		if not halted:
			print 'Simuation did not halt normally'

class CEmulatorWrapper:
	def __init__(self):
		self.EMULATOR_PATH = '../../tools/emulator/emulator'

	def runTest(self, filename):
		args = [ self.EMULATOR_PATH, filename ]

		try:
			process = subprocess.Popen(args, stdout=subprocess.PIPE)
			output = process.communicate()[0]
		except:
			print 'killing emulator process'
			process.kill()
			raise

		registerTraces = [ [] for x in range(4) ]
		for line in output.split('\n'):
			print line

			got = vectorRegPattern.match(line)
			if got:
				registerTraces[int(got.group('strand'))] += [ (got.group('pc'), got.group('reg'), got.group('mask'), got.group('value') ) ]
			else:
				got = scalarRegPattern.match(line)
				if got:
					registerTraces[int(got.group('strand'))] += [ (got.group('pc'), got.group('reg'), got.group('value') ) ]

		return registerTraces

if len(sys.argv) > 1:
	# Run on an existing file
	hexFilename = sys.argv[1]
else:
	# Generate a new random test file
	hexFilename = 'WORK/test.hex'
	Generator().generate(hexFilename)

print "generating reference trace"
model = CEmulatorWrapper()
modeltraces = model.runTest(hexFilename)
print modeltraces

print "running simulation"
sim = VerilogSimulatorWrapper()
simtraces = sim.runTest(hexFilename)
print simtraces

print "testing"

# XXX compare results