"""Base class for tests using a database."""

from qgis import processing
from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsApplication,
    QgsProviderRegistry,
)

from netads.processing_netads.provider import (
    NetAdsProvider as ProcessingProvider,
)
from netads.tests.base import BaseTestProcessing

__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from tests.feedbacks import FeedbackPrint

SCHEMA = "netads"


class DatabaseTestCase(BaseTestProcessing):

    """Base class for tests using a database."""

    def setUp(self) -> None:
        self.provider = None
        self.metadata = QgsProviderRegistry.instance().providerMetadata("postgres")

        self.connection = self.metadata.findConnection("test_database")
        self.connection: QgsAbstractDatabaseProviderConnection
        if SCHEMA in self.connection.schemas():
            self.connection.dropSchema(SCHEMA, True)
        self.feedback = FeedbackPrint()

        self.provider = ProcessingProvider()
        registry = QgsApplication.processingRegistry()
        if not registry.providerById(self.provider.id()):
            registry.addProvider(self.provider)

        params = {
            "CONNECTION_NAME": "test_database",
            "OVERRIDE": True,
            "CRS": "EPSG:2154",
        }
        processing.run(
            "{}:create_database_structure".format(self.provider.id()),
            params,
            feedback=None,
        )

    # def tearDown(self) -> None:
    #     time.sleep(1)
    #     super().tearDown()
