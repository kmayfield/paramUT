from paramUT import ParamTestCase, ParamTestProgram


class myTestCase(ParamTestCase):
    def parseUserArgs(self, params):
        self.debug = params.verbose
        self.other = params.other

    def test_set_debug(self):
        self.assertEqual(self.debug, True)
        self.assertEqual(self.other, None)


class myTestProgram(ParamTestProgram):
    def addUserArgs(self, parser):
        parser.add_option('-o', '--other', action='store',
                          help='some other parameter', default=None)
        parser.set_default('verbose', True)
        parser.epilog = 'Ex. python -m paramUT.tests.test_params myTestCase -v'
        parser.description = 'Execute a test of the parameter passing unittest'


def main():
    myTestProgram()

if __name__ == '__main__':
    main()