"""Base class algorithm."""

from abc import abstractmethod

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProviderConnectionException,
)
from qgis.PyQt.QtGui import QIcon

from netads.qgis_plugin_tools import resources_path

__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


class BaseProcessingAlgorithm(QgsProcessingAlgorithm):
    def createInstance(self):
        return type(self)()

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagHideFromModeler

    def icon(self) -> QIcon:
        icon = resources_path("icons", "icon.png")
        if icon.exists():
            return QIcon(str(icon))

        return super().icon()

    def parameters_help_string(self) -> str:
        """Return a formatted help string for all parameters."""
        help_string = ""
        for param in self.parameterDefinitions():
            info = param.help()
            if info:
                help_string += f"{param.name()} : {info}\n\n"

        return help_string

    @staticmethod
    def execute_sql(
            feedback: QgsProcessingFeedback,
            connection: QgsAbstractDatabaseProviderConnection,
            sql: str):
        """ Execute SQL, stop the algorithm in case of error. """
        try:
            connection.executeSql(sql)
        except QgsProviderConnectionException as e:
            connection.executeSql("ROLLBACK;")
            feedback.reportError("Erreur lors de la requête SQL suivante : <br>" + sql)
            raise QgsProcessingException(str(e))

    @abstractmethod
    def shortHelpString(self):
        pass
