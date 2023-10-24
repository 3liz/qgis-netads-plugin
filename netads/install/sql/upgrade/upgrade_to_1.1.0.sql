BEGIN;

-- Ajout de la contrainte d'unicité du champs ident pour la table parcelles
ALTER TABLE ONLY netads.parcelles
    DROP CONSTRAINT IF EXISTS parcelles_ident_unique;
ALTER TABLE ONLY netads.parcelles
    ADD CONSTRAINT parcelles_ident_unique UNIQUE (ident);


COMMIT;
