# This file is part sale_cancel_pending_moves module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest


from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite


class SaleCancelPendingMovesTestCase(ModuleTestCase):
    'Test Sale Cancel Pending Moves module'
    module = 'sale_cancel_pending_moves'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            SaleCancelPendingMovesTestCase))
    return suite
