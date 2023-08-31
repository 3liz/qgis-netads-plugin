__copyright__ = "Copyright 2023, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


from typing import Dict

from qgis.core import (
    QgsExpressionContextUtils,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterProviderConnection,
    QgsProviderRegistry,
)

from netads.processing_netads.data.base import BaseDataAlgorithm


class ImportCommunesAlg(BaseDataAlgorithm):
    """
    Import des données Parcellaires depuis le cadastre
    """

    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA_NETADS = "SCHEMA_NETADS"
    SCHEMA_CADASTRE = "SCHEMA_CADASTRE"
    TRUNCATE_PARCELLES = "TRUNCATE_PARCELLES"
    IMPORT_PROJECT_LAYER = "IMPORT_PROJECT_LAYER"
    OUTPUT = "OUTPUT"

    def name(self):
        return "data_commune"

    def displayName(self):
        return "Import des communes"

    def shortHelpString(self):
        return "Ajout des données pour la table communes"

    def initAlgorithm(self, config: Dict):
        # INPUTS
        # Database connection parameters
        label = "Connexion PostgreSQL vers la base de données"
        tooltip = "Base de données de destination"
        default = QgsExpressionContextUtils.globalScope().variable(
            "netads_connection_name"
        )
        # noinspection PyArgumentList
        param = QgsProcessingParameterProviderConnection(
            self.CONNECTION_NAME,
            label,
            "postgres",
            optional=False,
            defaultValue=default,
        )
        param.setHelp(tooltip)
        self.addParameter(param)

        label = "Schéma Cadastre"
        tooltip = "Nom du schéma des données cadastre"
        default = "cadastre"
        # noinspection PyArgumentList
        param = QgsProcessingParameterDatabaseSchema(
            self.SCHEMA_CADASTRE,
            label,
            self.CONNECTION_NAME,
            defaultValue=default,
            optional=False,
        )
        param.setHelp(tooltip)
        self.addParameter(param)

        label = "Schéma NetADS"
        tooltip = "Nom du schéma des données NetADS"
        default = "netads"
        # noinspection PyArgumentList
        param = QgsProcessingParameterDatabaseSchema(
            self.SCHEMA_NETADS,
            label,
            self.CONNECTION_NAME,
            defaultValue=default,
            optional=False,
        )
        param.setHelp(tooltip)
        self.addParameter(param)

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.TRUNCATE_PARCELLES, "Mise à jour de la table communes"
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.IMPORT_PROJECT_LAYER, "Importer la couche dans le projet"
            )
        )

        # OUTPUTS
        self.addOutput(
            QgsProcessingOutputMultipleLayers(self.OUTPUT, "Couches de sortie")
        )

    def processAlgorithm(
        self,
        parameters: Dict,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        schema_cadastre = self.parameterAsSchema(
            parameters, self.SCHEMA_CADASTRE, context
        )
        schema_netads = self.parameterAsSchema(
            parameters, self.SCHEMA_NETADS, context
        )

        data_update = self.parameterAsBool(parameters, self.TRUNCATE_PARCELLES, context)

        connection = metadata.findConnection(connection_name)
        if not connection:
            raise QgsProcessingException(
                f"La connexion {connection_name} n'existe pas."
            )

        if data_update:
            feedback.pushInfo("# Vide la table netads.communes #")
            sql = "TRUNCATE netads.communes RESTART IDENTITY;"
            self.execute_sql(feedback, connection, sql)

            feedback.pushInfo("## Mise à jour des données parcelles ##")

            sql = f"""
                INSERT INTO {schema_netads}.communes (anneemajic,codeinsee,ccodep,codcomm,nom,geom)
                SELECT cm.annee::int, ccodep || ccocom ,cm.ccodep, cm.ccocom, cm.libcom, gc.geom
                FROM {schema_cadastre}.commune_majic cm
                JOIN {schema_cadastre}.geo_commune gc on gc.commune = cm.commune;
            """
            self.execute_sql(feedback, connection, sql)

        import_layer = self.parameterAsBool(
            parameters, self.IMPORT_PROJECT_LAYER, context
        )

        output_layers = []
        if not import_layer:
            return {self.OUTPUT: output_layers}

        result_msg, uri = self.get_uri(connection)
        feedback.pushInfo(result_msg)

        feedback.pushInfo("")
        feedback.pushInfo("## CHARGEMENT DE LA COUCHE ##")

        name = "communes"
        result_msg, layer = self.import_layer(context, uri, schema_netads, name)
        feedback.pushInfo(result_msg)
        if layer:
            output_layers.append(layer.id())

        return {self.OUTPUT: output_layers}
