__copyright__ = 'Copyright 2023, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


from qgis.core import QgsApplication
from qgis.testing import unittest

from netads.processing_netads.provider import NetAdsProvider as Provider


class BaseTestProcessing(unittest.TestCase):

    """ Base test class for Processing. """
    qgs = None

    # noinspection PyCallByClass,PyArgumentList
    @classmethod
    def setUpClass(cls) -> None:
        from qgis.utils import iface

        if not iface:
            print("Init QGIS application")
            cls.qgs = QgsApplication([], False)
            cls.qgs.initQgis()
        else:
            cls.qgs = None

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.qgs:
            cls.qgs.exitQgis()

    def setUp(self) -> None:
        registry = QgsApplication.processingRegistry()

        self.provider = Provider()
        if not registry.providerById(self.provider.id()):
            registry.addProvider(self.provider)

    # def tearDown(self) -> None:
        # if self.provider:
        #     QgsApplication.processingRegistry().removeProvider(self.provider)
