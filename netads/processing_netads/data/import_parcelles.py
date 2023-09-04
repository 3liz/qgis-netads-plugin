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
    QgsProviderConnectionException,
    QgsProviderRegistry,
)

from netads.processing_netads.data.base import BaseDataAlgorithm


class ImportParcellesAlg(BaseDataAlgorithm):
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
        return "data_parcelle"

    def displayName(self):
        return "Import des parcelles"

    def shortHelpString(self):
        return "Ajout des données pour la table parcelles"

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
                self.TRUNCATE_PARCELLES, "Mise à jour de la table parcelles"
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
        schema_netads = self.parameterAsSchema(parameters, self.SCHEMA_NETADS, context)

        data_update = self.parameterAsBool(parameters, self.TRUNCATE_PARCELLES, context)

        connection = metadata.findConnection(connection_name)
        if not connection:
            raise QgsProcessingException(
                f"La connexion {connection_name} n'existe pas."
            )

        if data_update:
            feedback.pushInfo("## Mise à jour des données parcelles ##")

            sql = f"""
                INSERT INTO {schema_netads}.parcelles (ccocom,ccodep,ccodir,ccopre,
                    ccosec,dnupla,geom,ident,ndeb,sdeb,nom,type)
                    SELECT p.ccocom, p.ccodep, p.ccodir, p.ccopre, p.ccosec, p.dnupla, pi.geom,
                           p.parcelle AS ident, p.dnvoiri, p.dindic, v.libvoi, v.natvoi
                    FROM {schema_cadastre}.parcelle p
                    JOIN {schema_cadastre}.parcelle_info pi on pi.geo_parcelle = p.parcelle
                    JOIN {schema_cadastre}.voie v on v.voie = pi.voie
                ON CONFLICT (ident) DO UPDATE SET
                    ccocom=EXCLUDED.ccocom, ccodep=EXCLUDED.ccodep,
                    ccodir=EXCLUDED.ccodir, ccopre=EXCLUDED.ccopre,
                    ccosec=EXCLUDED.ccosec, dnupla=EXCLUDED.dnupla,
                    geom=EXCLUDED.geom, ndeb=EXCLUDED.ndeb, sdeb=EXCLUDED.sdeb,
                    nom=EXCLUDED.nom, type=EXCLUDED.type;
            """
            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                _ = e
                connection.executeSql("ROLLBACK;")
                return {self.OUTPUT: []}

            feedback.pushInfo(
                f"# Suppression des parcelles dans {schema_netads}.parcelle qui n'existent plus #"
            )
            sql = f"""
                DELETE FROM {schema_netads}.parcelles
                WHERE ident NOT IN (
                    SELECT p.parcelle
                    FROM {schema_cadastre}.parcelle p
                )
            """
            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                _ = e
                connection.executeSql("ROLLBACK;")
                return {self.OUTPUT: []}

        import_layer = self.parameterAsBool(
            parameters, self.IMPORT_PROJECT_LAYER, context
        )

        output_layers = []
        if import_layer:
            result_msg, uri = self.get_uri(connection)
            feedback.pushInfo(result_msg)

            feedback.pushInfo("")
            feedback.pushInfo("## CHARGEMENT DE LA COUCHE ##")

            name = "parcelles"
            result_msg, layer = self.import_layer(context, uri, schema_netads, name)
            feedback.pushInfo(result_msg)
            if layer:
                output_layers.append(layer.id())

        return {self.OUTPUT: output_layers}
