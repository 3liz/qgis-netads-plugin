__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from unittest import TestCase

import processing

from qgis.core import QgsApplication
from tests.feedbacks import FeedbackPrint

from netads.processing_netads.provider import (
    NetAdsProvider as ProcessingProvider,
)


class TestCasePlugin(TestCase):

    qgs = None

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
        provider = ProcessingProvider()
        registry = QgsApplication.processingRegistry()
        if not registry.providerById(provider.id()):
            registry.addProvider(provider)

        params = {
            "CONNECTION_NAME": "test_database",
            "OVERRIDE": True,
            "CRS": "EPSG:2154",
        }
        alg = "{}:create_database_structure".format(provider.id())
        processing.run(alg, params, feedback=FeedbackPrint())
