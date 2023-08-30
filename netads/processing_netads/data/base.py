__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from collections import namedtuple
from typing import Optional, Tuple, Union

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsDataSourceUri,
    QgsProcessingContext,
    QgsVectorLayer,
)

from netads.processing_netads.base import BaseProcessingAlgorithm


class Layer(namedtuple('Layer', ['id', 'geom'])):
    pass


class BaseDataAlgorithm(BaseProcessingAlgorithm):

    OUTPUT = None

    def __init__(self):
        """Constructor."""
        super().__init__()
        self.layers_name = dict()
        self.layers_name["communes"] = Layer("id_communes", "geom")
        self.layers_name["parcelles"] = Layer("id_parcelles", "geom")
        self.layers_name["impacts"] = Layer("id_impacts", None)

    def group(self):
        return "Import des données"

    def groupId(self):
        return "data"

    def init_layer(
        self,
        context: QgsProcessingContext,
        uri: QgsDataSourceUri,
        schema: str,
        table: str,
        geom: Optional[str],
        sql: str,
        pk: str = None,
    ) -> Union[QgsVectorLayer, bool]:
        """Create vector layer from database table"""
        if geom is None:
            geom = ""

        if pk:
            uri.setDataSource(schema, table, geom, sql, pk)
        else:
            uri.setDataSource(schema, table, geom, sql)

        layer = QgsVectorLayer(uri.uri(), table, "postgres")

        if not layer.isValid():
            return False

        context.temporaryLayerStore().addMapLayer(layer)
        context.addLayerToLoadOnCompletion(
            layer.id(),
            QgsProcessingContext.LayerDetails(table, context.project(), self.OUTPUT),
        )
        return layer

    @staticmethod
    def get_uri(
        connection: QgsAbstractDatabaseProviderConnection,
    ) -> Tuple[str, QgsDataSourceUri]:
        """Function to get URI"""
        uri = QgsDataSourceUri(connection.uri())

        if uri.host() != "":
            msg = "Connexion établie via l'hôte"
        else:
            msg = "Connexion établie via le service"

        return msg, uri

    def import_layer(
        self,
        context: QgsProcessingContext,
        uri: QgsDataSourceUri,
        schema: str,
        name: str,
    ) -> Tuple[str, Union[bool, QgsVectorLayer]]:
        """Function to import layer"""
        if context.project().mapLayersByName(name):
            return f"La couche {name} est déjà présente", False

        result = self.init_layer(
            context,
            uri,
            schema,
            name,
            self.layers_name[name].geom,
            "",
            self.layers_name[name].id,
        )
        if not result:
            return f"La couche {name} ne peut pas être chargée", False
        else:
            return f"La couche {name} a pu être chargée", result
