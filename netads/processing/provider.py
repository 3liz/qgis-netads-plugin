__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from netads.processing.data.import_communes import ImportCommunesAlg
from netads.processing.database.create import CreateDatabaseStructure
from netads.processing.database.upgrade import UpgradeDatabaseStructure
from netads.qgis_plugin_tools import resources_path


class NetAdsProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        # Database
        self.addAlgorithm(CreateDatabaseStructure())
        self.addAlgorithm(UpgradeDatabaseStructure())
        # Data
        self.addAlgorithm(ImportCommunesAlg())

    def id(self):  # NOQA: A003
        return "netads"

    def icon(self):
        return QIcon(str(resources_path("icons", "icon.png")))

    def name(self):
        return "NetADS"

    def longName(self):
        return self.name()
