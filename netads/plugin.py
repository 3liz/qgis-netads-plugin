__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.utils import iface

from netads.processing_netads.provider import NetAdsProvider
from netads.qgis_plugin_tools import resources_path

URL_DOCUMENTATION = "https://docs.3liz.org/"


class NetAdsPlugin:

    """Main entry point of the plugin."""

    def __init__(self):
        """Constructor."""
        self.provider = None
        self.help_action = None

    def initProcessing(self):  # pylint: disable=invalid-name
        """Init the processing provider."""
        if not self.provider:
            self.provider = NetAdsProvider()
            QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):  # pylint: disable=invalid-name
        """Init the GUI."""
        self.initProcessing()

        icon = QIcon(str(resources_path("icons", "icon.png")))

        # Open the online help
        self.help_action = QAction(icon, "NetADS", iface.mainWindow())
        iface.pluginHelpMenu().addAction(self.help_action)
        self.help_action.triggered.connect(self.open_help)

    def unload(self) -> None:
        """Unload the plugin from QGIS."""
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

        if self.help_action:
            iface.pluginHelpMenu().removeAction(self.help_action)
            del self.help_action

    @staticmethod
    def open_help():
        """Open the online help."""
        QDesktopServices.openUrl(QUrl(URL_DOCUMENTATION))
