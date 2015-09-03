#!/usr/bin/python
#
# disksnoop.py	Trace block device I/O: basic version of iosnoop.
#		For Linux, uses BCC, eBPF. See .c file.
#
# Written as a basic example of tracing latency.
#
# Copyright (c) 2015 Brendan Gregg.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 11-Aug-2015	Brendan Gregg	Created this.

from __future__ import print_function
from bcc import BPF
import sys

REQ_WRITE = 1		# from include/linux/blk_types.h

# load BPF program
b = BPF(src_file="disksnoop.c")
b.attach_kprobe(event="blk_start_request", fn_name="do_request")
b.attach_kprobe(event="blk_update_request", fn_name="do_completion")

# header
print("%-18s %-2s %-7s %8s" % ("TIME(s)", "T", "BYTES", "LAT(ms)"))

# open trace pipe
try:
	trace = open("/sys/kernel/debug/tracing/trace_pipe", "r")
except:
	print("ERROR: opening trace_pipe", file=sys.stderr)
	exit(1)

# format output
while 1:
	(task, pid, cpu, flags, ts, msg) = b.trace_readline_fields()
	(bytes_s, bflags_s, us_s) = msg.split()

	if int(bflags_s, 16) & REQ_WRITE:
		type_s = "W"
	elif bytes_s == "0":	# see blk_fill_rwbs() for logic
		type_s = "M"
	else:
		type_s = "R"
	ms = float(int(us_s, 10)) / 1000

	print("%-18.9f %-2s %-7s %8.2f" % (ts, type_s, bytes_s, ms))
