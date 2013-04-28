#!/usr/bin/env python

#
# Module that run unitests
#
import unittest
from christinetests.christineConf import cconf

suite = unittest.makeSuite(cconf)
unittest.TextTestRunner(verbosity=2).run(suite)