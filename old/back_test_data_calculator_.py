import unittest
from bytes_helper import DataSizeCalculator, data_size_calculator
from bytes_helper_lookups import *

def _test_equal(a, b):
    assert a == b

def run_dsc_test(dsc_params=None, call_params=None, **dso_validations):
    base_msg = 'dsc'
    if dsc_params is not None and dsc_params != {}:
        dsc = DataSizeCalculator(**dsc_params)
        base_msg += '%r' % dsc_params
    else:
        dsc = data_size_calculator

    if call_params is not None and call_params is not {}:
        base_msg += '%r' % call_params

    base_msg = base_msg.replace('{', '(').replace('}', ')')
    tmp_check = dsc(**dsc_params)

    for key, value in dso_validations.items():
        tmp_validation = getattr(tmp_check, key)
        msg = '%s.%s = %s, expected: %s  (dso:%r)' % (base_msg, key, tmp_validation, value, tmp_check)
        '''
        with self.subTest(m=msg):
            assertEqual(value, tmp_validation)
        '''
        yield _test_equal, value, tmp_check

def run_dsc_raise_test(self, dsc_params=None, call_params=None, exception=AttributeError):
    base_msg = 'dsc'
    if dsc_params is not None and dsc_params != {}:
        dsc = DataSizeCalculator(**dsc_params)
        base_msg += '%r' % dsc_params
    else:
        dsc = data_size_calculator

    if call_params is not None and call_params is not {}:
        base_msg += '%r' % call_params

    base_msg = base_msg.replace('{', '(').replace('}', ')')
    base_msg += ' Should have raised an exception'

    with self.subTest(m=base_msg):
        with self.assertRaises(exception):
            tmp_check = dsc(**dsc_params)

def run_tests(run_set=None, raise_set=None):
    if run_set is not None:
        for test in run_set:
            run_dsc_test(dsc_params=test[0], call_params=test[1], **test[2])
    if raise_set is not None:
        for test in raise_set:
            tmp_params = {}
            if len(test) == 1:
                tmp_params['call_params'] = test[0]
            elif len(test) > 1:
                tmp_params['dsc_params'] = test[0]
                tmp_params['call_params'] = test[1]

            if len(test) == 3:
                tmp_params['exception'] = test[2]

            run_dsc_raise_test(**tmp_params)

def test_parse():
    test_set = [
        # normal
        ({}, {'value': '2Mb'}, {'value': 2, 'unit': 'Mb'}),
        ({}, {'value': '2-Mb'}, {'value': 2, 'unit': 'Mb'}),
        ({}, {'value': '332-Mb'}, {'value': 2, 'unit': 'Mb'}),
        ({}, {'value': '.2-Mb'}, {'value': 0.2, 'unit': 'Mb'}),
        ({}, {'value': '0.2-Mb'}, {'value': 0.2, 'unit': 'Mb'}),
        ({}, {'value': '-2-Mb'}, {'value': -2, 'unit': 'Mb'}),


        # override units
        ({}, {'value': '0.2-Mb', 'unit': 'Kb'}, {'value': 0.2, 'unit': 'Kb'}),
        ({}, {'value': '-2-Mb', 'unit': 'MiB'}, {'value': -2, 'unit': 'MiB'}),

        # include long names
        ({}, {'value': '0.2-Megabits'}, {'value': 0.2, 'unit': 'Kb'}),
        ({}, {'value': '39 KiloBytes'}, {'value': 39, 'unit': 'KB'}),

        # include basic suffix
        ({}, {'value': '0.2-Megabits/sec'}, {'value': 0.2, 'unit': 'Kb', 'suffix': '/s'}),
        ({}, {'value': '0.2-Megabits/s'}, {'value': 0.2, 'unit': 'Kb', 'suffix': '/s'}),

        # override suffix
        ({}, {'value': '0.2-Mb', 'unit': 'Kb', 'suffix': '/s'}, {'value': 0.2, 'unit': 'Kb', 'suffix': '/s'}),
        ({}, {'value': '0.2-Gb', 'suffix': '/s'}, {'value': 0.2, 'unit': 'Gb', 'suffix': '/s'}),
        ({}, {'value': '0.2-Gb/min', 'suffix': '/s'}, {'value': 0.2, 'unit': 'Gb', 'suffix': '/s'}),


        # include case problems with unitset
        ({}, {'value': '2mb', 'unitset': DEC_BYT}, {'value': 2, 'unit': 'MB'}),
        ({}, {'value': '2m', 'unitset': DEC_BIT}, {'value': 2, 'unit': 'Mb'}),
        ({}, {'value': '332-b', 'unitset': DEC_BYT}, {'value': 2, 'unit': 'B'}),
        ({}, {'value': '.2-Mb', 'unitset': BIN_BYT}, {'value': 0.2, 'unit': 'MiB'}),
        ({}, {'value': '0.2-Mb', 'unitset': BIN_BIT}, {'value': 0.2, 'unit': 'Mib'}),
        ({}, {'value': '.2-meg', 'unitset': BIN_BYT}, {'value': 0.2, 'unit': 'MB'}),
        ({}, {'value': '0.2-gig', 'unitset': BIN_BIT}, {'value': 0.2, 'unit': 'Gib'}),

        # detect unitset
        ({}, {'value': '2Mb'}, {'value': 2, 'unit': 'Mb', 'unitset': None}),
        ({}, {'value': '2-MB'}, {'value': 2, 'unit': 'Mb', 'unitset': DEC_BYT}),
        ({}, {'value': '332-gig'}, {'value': 2, 'unit': 'Mb', 'unitset': DEC_BYT}),
        ({}, {'value': '.2-Mb'}, {'value': 0.2, 'unit': 'Mb', 'unitset': DEC_BYT}),
        ({}, {'value': '0.2-Mb'}, {'value': 0.2, 'unit': 'Mb', 'unitset': DEC_BYT}),
        ({}, {'value': '-2-Mb'}, {'value': -2, 'unit': 'Mb', 'unitset': DEC_BIT}),

    ]

    test_raises = [
        ({'value': '2'},),
        ({'value': 2},),
        ({'value': 'blah'},),
        ({'value': '2', 'suffix': '/s'},),
        ({'value': 2, 'suffix': '/s'},),
    ]

    run_tests(test_set)


class TestDSC(object):

    def _run_dsc_test(self, dsc_params=None, call_params=None, **dso_validations):
        base_msg = 'dsc'
        if dsc_params is not None and dsc_params != {}:
            dsc = DataSizeCalculator(**dsc_params)
            base_msg += '%r' % dsc_params
        else:
            dsc = data_size_calculator

        if call_params is not None and call_params is not {}:
            base_msg += '%r' % call_params

        base_msg = base_msg.replace('{', '(').replace('}', ')')
        tmp_check = dsc(**dsc_params)

        for key, value in dso_validations.items():
            tmp_validation = getattr(tmp_check, key)
            msg = '%s.%s = %s, expected: %s  (dso:%r)' % (base_msg, key, tmp_validation, value, tmp_check)
            with self.subTest(m=msg):
                self.assertEqual(value, tmp_validation)

    def _run_dsc_raise_test(self, dsc_params=None, call_params=None, exception=AttributeError):
        base_msg = 'dsc'
        if dsc_params is not None and dsc_params != {}:
            dsc = DataSizeCalculator(**dsc_params)
            base_msg += '%r' % dsc_params
        else:
            dsc = data_size_calculator

        if call_params is not None and call_params is not {}:
            base_msg += '%r' % call_params

        base_msg = base_msg.replace('{', '(').replace('}', ')')
        base_msg += ' Should have raised an exception'

        with self.subTest(m=base_msg):
            with self.assertRaises(exception):
                tmp_check = dsc(**dsc_params)

    def run_tests(self, run_set=None, raise_set=None):
        if run_set is not None:
            for test in run_set:
                self._run_dsc_test(dsc_params=test[0], call_params=test[1], **test[2])
        if raise_set is not None:
            for test in raise_set:
                tmp_params = {}
                if len(test) == 1:
                    tmp_params['call_params'] = test[0]
                elif len(test) > 1:
                    tmp_params['dsc_params'] = test[0]
                    tmp_params['call_params'] = test[1]

                if len(test) == 3:
                    tmp_params['exception'] = test[2]

                self._run_dsc_raise_test(**tmp_params)

    def test_parse(self):
        test_set = [
            # normal
            ({}, {'value': '2Mb'}, {'value': 2, 'unit': 'Mb'}),
            ({}, {'value': '2-Mb'}, {'value': 2, 'unit': 'Mb'}),
            ({}, {'value': '332-Mb'}, {'value': 2, 'unit': 'Mb'}),
            ({}, {'value': '.2-Mb'}, {'value': 0.2, 'unit': 'Mb'}),
            ({}, {'value': '0.2-Mb'}, {'value': 0.2, 'unit': 'Mb'}),
            ({}, {'value': '-2-Mb'}, {'value': -2, 'unit': 'Mb'}),


            # override units
            ({}, {'value': '0.2-Mb', 'unit': 'Kb'}, {'value': 0.2, 'unit': 'Kb'}),
            ({}, {'value': '-2-Mb', 'unit': 'MiB'}, {'value': -2, 'unit': 'MiB'}),

            # include long names
            ({}, {'value': '0.2-Megabits'}, {'value': 0.2, 'unit': 'Kb'}),
            ({}, {'value': '39 KiloBytes'}, {'value': 39, 'unit': 'KB'}),

            # include basic suffix
            ({}, {'value': '0.2-Megabits/sec'}, {'value': 0.2, 'unit': 'Kb', 'suffix': '/s'}),
            ({}, {'value': '0.2-Megabits/s'}, {'value': 0.2, 'unit': 'Kb', 'suffix': '/s'}),

            # override suffix
            ({}, {'value': '0.2-Mb', 'unit': 'Kb', 'suffix': '/s'}, {'value': 0.2, 'unit': 'Kb', 'suffix': '/s'}),
            ({}, {'value': '0.2-Gb', 'suffix': '/s'}, {'value': 0.2, 'unit': 'Gb', 'suffix': '/s'}),
            ({}, {'value': '0.2-Gb/min', 'suffix': '/s'}, {'value': 0.2, 'unit': 'Gb', 'suffix': '/s'}),


            # include case problems with unitset
            ({}, {'value': '2mb', 'unitset': DEC_BYT}, {'value': 2, 'unit': 'MB'}),
            ({}, {'value': '2m', 'unitset': DEC_BIT}, {'value': 2, 'unit': 'Mb'}),
            ({}, {'value': '332-b', 'unitset': DEC_BYT}, {'value': 2, 'unit': 'B'}),
            ({}, {'value': '.2-Mb', 'unitset': BIN_BYT}, {'value': 0.2, 'unit': 'MiB'}),
            ({}, {'value': '0.2-Mb', 'unitset': BIN_BIT}, {'value': 0.2, 'unit': 'Mib'}),
            ({}, {'value': '.2-meg', 'unitset': BIN_BYT}, {'value': 0.2, 'unit': 'MB'}),
            ({}, {'value': '0.2-gig', 'unitset': BIN_BIT}, {'value': 0.2, 'unit': 'Gib'}),

            # detect unitset
            ({}, {'value': '2Mb'}, {'value': 2, 'unit': 'Mb', 'unitset': None}),
            ({}, {'value': '2-MB'}, {'value': 2, 'unit': 'Mb', 'unitset': DEC_BYT}),
            ({}, {'value': '332-gig'}, {'value': 2, 'unit': 'Mb', 'unitset': DEC_BYT}),
            ({}, {'value': '.2-Mb'}, {'value': 0.2, 'unit': 'Mb', 'unitset': DEC_BYT}),
            ({}, {'value': '0.2-Mb'}, {'value': 0.2, 'unit': 'Mb', 'unitset': DEC_BYT}),
            ({}, {'value': '-2-Mb'}, {'value': -2, 'unit': 'Mb', 'unitset': DEC_BIT}),

        ]

        test_raises = [
            ({'value': '2'},),
            ({'value': 2},),
            ({'value': 'blah'},),
            ({'value': '2', 'suffix': '/s'},),
            ({'value': 2, 'suffix': '/s'},),
        ]

        self.run_tests(test_set, test_raises)

