"""
The runner application is a unittest based test framework used to perform
unit tests and functional tests on the wordCount application.  The runner
script validates the wordCount output using both known good baseline
data, as well as Unix command-line tools that generate similar word count
output.

The runner application does error checking as well to ensure the wordCount
application informs the user when he/she enters erroneous input.  The runner
also checks that the wordCount application can handle unicode input.
"""
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
import sys
import unittest
import logging
from unittest.main import FAILFAST, CATCHBREAK, BUFFEROUTPUT

if sys.version_info[0] == 2:
    from ConfigParser import ConfigParser
elif sys.version_info[0] == 3:
    from configparser import ConfigParser
else:
    print ("python%s is not supported." % sys.version_info[0])


class ParamTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(ParamTestCase, self).__init__(methodName=methodName)
        self.user_params = None

    def parseUserArgs(self, params):
        raise NotImplementedError

    def setUp(self):
        self.parseUserArgs(self.user_params)
        super(ParamTestCase, self).setUp()


class ParamTestLoader(unittest.TestLoader):
    def addParams(self, tests, params):
        for test in tests:
            test.user_params = params
        return tests

    def loadTestsFromModule(self, module, use_load_tests=True, params=None):
        tests = super(ParamTestLoader, self).loadTestsFromModule(module,
                                                                use_load_tests)
        return self.addParams(tests, params)

    def loadTestsFromName(self, name, module=None, params=None):
        tests = super(ParamTestLoader, self).loadTestsFromName(name, module)
        return self.addParams(tests, params)

    def loadTestsFromNames(self, names, module=None, params=None):
        """Return a suite of all tests cases found using the given sequence
        of string specifiers. See 'loadTestsFromName()'.
        """
        suites = [self.loadTestsFromName(name, module, params)
                  for name in names]
        return self.suiteClass(suites)


class ParamTestProgram(unittest.TestProgram):
    def __init__(self, *args, **kwargs):
        kwargs.update({'testLoader': ParamTestLoader()})
        super(ParamTestProgram, self).__init__(*args, **kwargs)

    def addUserArgs(self, args):
        """Should return any args not needed by the user test program."""
        self.user_params = None
        raise NotImplementedError

    def parseArgs(self, argv):
        if len(argv) > 1 and argv[1].lower() == 'discover':
            self._do_discovery(argv[2:])
            return

        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option('-v', '--verbose', action='store_true',
                          help='Turn on debug output', default=False)
        parser.add_option('-q', '--quiet', action='store_true',
                          help='Turn off debug output', default=False)
        parser.add_option('-f', '--failfast', action='store_true',
                          help=FAILFAST.rsplit('   ')[-1], default=False)
        parser.add_option('-c', '--catchbreak', action='store_true',
                          help=CATCHBREAK.rsplit('   ')[-1], default=False)
        parser.add_option('-b', '--buffer', action='store_true',
                          help=BUFFEROUTPUT.rsplit('   ')[-1], default=False)
        self.addUserArgs(parser)
        self.user_params, args = parser.parse_args()

        self.verbosity = 1
        level = logging.INFO

        if self.user_params.__dict__.pop('quiet'):
            self.verbosity = 0
            level = logging.ERROR
        elif self.user_params.verbose:
            self.verbosity = 2
            level = logging.DEBUG
         
        logging.basicConfig(filename='runner.log',
                            filemode='w+', level=level)

        self.failfast = self.user_params.__dict__.pop('failfast')
        self.catchbreak = self.user_params.__dict__.pop('catchbreak')
        self.buffer = self.user_params.__dict__.pop('buffer')

        if len(args) == 0 and self.defaultTest is None:
            # createTests will load tests from self.module
            self.testNames = None
        elif len(args) > 0:
            self.testNames = args
            if __name__ == '__main__':
                # to support python -m unittest ...
                self.module = None
        else:
            self.testNames = (self.defaultTest,)
        self.createTests()
         
    def createTests(self):
        if self.testNames is None:
            self.test = self.testLoader.loadTestsFromModule(self.module,
                                                     params=self.user_params)
        else:
            self.test = self.testLoader.loadTestsFromNames(self.testNames,
                                                     self.module,
                                                     params=self.user_params)
