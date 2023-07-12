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
    id_communes integer NOT NULL,
    anneemajic integer,
    ccodep text,
    codcomm text,
    nom text,
    codeinsee character(5) NOT NULL,
    created_user text,
    created_date date,
    last_edited_user text,
    last_edited_date date,
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


-- parcelles
CREATE TABLE netads.parcelles (
    id_parcelles integer NOT NULL,
    ccocom text,
    ccodep text,
    ccodir text,
    ccopre text,
    ccosec text,
    dnupla text,
    ident text,
    ndeb text,
    sdeb text,
    nom text,
    type text,
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
    id integer NOT NULL,
    version text NOT NULL,
    version_date date NOT NULL,
    status smallint NOT NULL
);


-- communes id_communes
ALTER TABLE ONLY netads.communes ALTER COLUMN id_communes SET DEFAULT nextval('netads.communes_id_communes_seq'::regclass);


-- parcelles id_parcelles
ALTER TABLE ONLY netads.parcelles ALTER COLUMN id_parcelles SET DEFAULT nextval('netads.parcelles_id_parcelles_seq'::regclass);


--
-- PostgreSQL database dump complete
--


COMMIT;
