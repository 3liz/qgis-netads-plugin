__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from netads.processing_netads.data.import_communes import ImportCommunesAlg

# from netads.processing_netads.data.import_impacts import ImportImpactsAlg
from netads.processing_netads.data.import_parcelles import ImportParcellesAlg
from netads.processing_netads.data.load_layers import LoadLayersAlgorithm
from netads.processing_netads.database.create import CreateDatabaseStructure
from netads.processing_netads.database.upgrade import UpgradeDatabaseStructure
from netads.qgis_plugin_tools import resources_path


class NetAdsProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        # Database
        self.addAlgorithm(CreateDatabaseStructure())
        self.addAlgorithm(UpgradeDatabaseStructure())
        # Data
        self.addAlgorithm(ImportCommunesAlg())
        # self.addAlgorithm(ImportImpactsAlg())
        self.addAlgorithm(ImportParcellesAlg())
        self.addAlgorithm(LoadLayersAlgorithm())

    def id(self):  # NOQA: A003
        return "netads"

    def icon(self):
        return QIcon(str(resources_path("icons", "icon.png")))

    def name(self):
        return "NetADS"

    def longName(self):
        return self.name()
