BEGIN;
--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3 (Debian 15.3-1.pgdg110+1)
-- Dumped by pg_dump version 15.3 (Debian 15.3-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';



-- communes
CREATE TABLE netads.communes (
    id_communes INTEGER NOT NULL,
    anneemajic INTEGER,
    ccodep TEXT,
    codcomm TEXT,
    nom TEXT,
    codeinsee CHARACTER(5) NOT NULL,
    created_user TEXT,
    created_date DATE,
    last_edited_user TEXT,
    last_edited_date DATE,
    geom public.geometry(MultiPolygon,2154)
);


-- communes_id_communes_seq
CREATE SEQUENCE netads.communes_id_communes_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- communes_id_communes_seq
ALTER SEQUENCE netads.communes_id_communes_seq OWNED BY netads.communes.id_communes;


-- geo_impacts
CREATE TABLE netads.geo_impacts (
    id_geo_impacts INTEGER NOT NULL,
    id_impacts INTEGER NOT NULL,
    libelle TEXT,
    codeinsee CHARACTER(5) NOT NULL,
    geom public.geometry(Polygon,2154)
);


-- geo_impacts_id_geo_impacts_seq
CREATE SEQUENCE netads.geo_impacts_id_geo_impacts_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- geo_impacts_id_geo_impacts_seq
ALTER SEQUENCE netads.geo_impacts_id_geo_impacts_seq OWNED BY netads.geo_impacts.id_geo_impacts;


-- impacts
CREATE TABLE netads.impacts (
    id_impacts INTEGER NOT NULL,
    type text NOT NULL,
    code CHARACTER VARYING(10) NOT NULL,
    sous_code CHARACTER VARYING(10),
    etiquette CHARACTER VARYING(10),
    libelle CHARACTER VARYING(255) NOT NULL,
    description TEXT,
    CONSTRAINT check_type CHECK ((type = ANY (ARRAY['ZONAGE'::text, 'SERVITUDE'::text, 'PRESCRIPTION'::text, 'INFORMATION'::text])))
);


-- impacts_id_impacts_seq
CREATE SEQUENCE netads.impacts_id_impacts_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- impacts_id_impacts_seq
ALTER SEQUENCE netads.impacts_id_impacts_seq OWNED BY netads.impacts.id_impacts;


-- parcelles
CREATE TABLE netads.parcelles (
    id_parcelles INTEGER NOT NULL,
    ccocom TEXT,
    ccodep TEXT,
    ccodir TEXT,
    ccopre TEXT,
    ccosec TEXT,
    dnupla TEXT,
    ident TEXT,
    ndeb TEXT,
    sdeb TEXT,
    nom TEXT,
    type TEXT,
    geom public.geometry(MultiPolygon,2154)
);


-- parcelles_id_parcelles_seq
CREATE SEQUENCE netads.parcelles_id_parcelles_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- parcelles_id_parcelles_seq
ALTER SEQUENCE netads.parcelles_id_parcelles_seq OWNED BY netads.parcelles.id_parcelles;


-- qgis_plugin
CREATE TABLE netads.qgis_plugin (
    id INTEGER NOT NULL,
    version TEXT NOT NULL,
    version_date DATE NOT NULL,
    status SMALLINT NOT NULL
);


-- communes id_communes
ALTER TABLE ONLY netads.communes ALTER COLUMN id_communes SET DEFAULT nextval('netads.communes_id_communes_seq'::regclass);


-- geo_impacts id_geo_impacts
ALTER TABLE ONLY netads.geo_impacts ALTER COLUMN id_geo_impacts SET DEFAULT nextval('netads.geo_impacts_id_geo_impacts_seq'::regclass);


-- impacts id_impacts
ALTER TABLE ONLY netads.impacts ALTER COLUMN id_impacts SET DEFAULT nextval('netads.impacts_id_impacts_seq'::regclass);


-- parcelles id_parcelles
ALTER TABLE ONLY netads.parcelles ALTER COLUMN id_parcelles SET DEFAULT nextval('netads.parcelles_id_parcelles_seq'::regclass);


--
-- PostgreSQL database dump complete
--


COMMIT;
