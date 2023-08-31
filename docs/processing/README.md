---
hide:
  - navigation
---

# Processing

## Base de données


### Installation de la base de données

Création de la structure de la base données. 

![algo_id](./netads-create_database_structure.jpg)

#### Parameters

| ID | Description | Type | Info | Required | Advanced | Option |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
CONNECTION_NAME|Connexion PostgreSQL vers la base de données|ProviderConnection|Nom de la connexion dans QGIS pour se connecter à la base de données|✓|||
CRS|Projection|Crs||✓||Default: EPSG:2154 <br> |
OVERRIDE|Écraser le schéma netads ? ** ATTENTION ** Cela supprimera toutes les données !|Boolean||✓|||


#### Outputs

| ID | Description | Type | Info |
|:-:|:-:|:-:|:-:|
DATABASE_VERSION|Version de la base de données|String||


***


### Mise à jour de la base de données

Mise à jour de la structure de la base données. 

![algo_id](./netads-upgrade_database_structure.jpg)

#### Parameters

| ID | Description | Type | Info | Required | Advanced | Option |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
CONNECTION_NAME|Connexion PostgreSQL vers la base de données|ProviderConnection|Nom de la connexion dans QGIS pour se connecter à la base de données|✓|||
CRS|Projection|Crs||✓||Default: EPSG:2154 <br> |
RUN_MIGRATIONS|Cocher cette option pour lancer la mise-à-jour.|Boolean||✓|||


#### Outputs

| ID | Description | Type | Info |
|:-:|:-:|:-:|:-:|
OUTPUT_STATUS|Output status|Number||
OUTPUT_STRING|Output message|String||


***


## Import des données


### Import des communes

Ajout des données pour la table communes

![algo_id](./netads-data_commune.jpg)

#### Parameters

| ID | Description | Type | Info | Required | Advanced | Option |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
CONNECTION_NAME|Connexion PostgreSQL vers la base de données|ProviderConnection|Base de données de destination|✓|||
SCHEMA_CADASTRE|Schéma Cadastre|DatabaseSchema|Nom du schéma des données cadastre|✓||Default: cadastre <br> |
SCHEMA_NETADS|Schéma NetADS|DatabaseSchema|Nom du schéma des données NetADS|✓||Default: netads <br> |
TRUNCATE_PARCELLES|Mise à jour de la table communes|Boolean||✓|||
IMPORT_PROJECT_LAYER|Importer la couche dans le projet|Boolean||✓|||


#### Outputs

| ID | Description | Type | Info |
|:-:|:-:|:-:|:-:|
OUTPUT|Couches de sortie|MultipleLayers||
OUTPUT MSG|Message de sortie|String||


***


### Chargement des couches depuis la base

Charger les couches de la base de données.

![algo_id](./netads-load_layers.jpg)

#### Parameters

| ID | Description | Type | Info | Required | Advanced | Option |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
CONNECTION_NAME|Connexion PostgreSQL vers la base de données|ProviderConnection|Base de données où sont stockés les données|✓|||
SCHEMA|Schéma|DatabaseSchema|Nom du schéma des données netads|✓||Default: netads <br> |
CODE_CLIENT|Code client NetADS|String|Code client NetADS attribué à la collectivité||||


#### Outputs

| ID | Description | Type | Info |
|:-:|:-:|:-:|:-:|
OUTPUT|Couches de sortie|MultipleLayers||


***

