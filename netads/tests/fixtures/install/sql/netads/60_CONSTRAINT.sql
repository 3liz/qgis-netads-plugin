BEGIN;
--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4 (Debian 15.4-1.pgdg110+1)
-- Dumped by pg_dump version 15.4 (Debian 15.4-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

-- communes communes_pkey
ALTER TABLE ONLY netads.communes
    ADD CONSTRAINT communes_pkey PRIMARY KEY (id_communes);


-- geo_impacts geo_impacts_pkey
ALTER TABLE ONLY netads.geo_impacts
    ADD CONSTRAINT geo_impacts_pkey PRIMARY KEY (id_geo_impacts);


-- impacts impacts_pkey
ALTER TABLE ONLY netads.impacts
    ADD CONSTRAINT impacts_pkey PRIMARY KEY (id_impacts);


-- parcelles parcelles_pkey
ALTER TABLE ONLY netads.parcelles
    ADD CONSTRAINT parcelles_pkey PRIMARY KEY (id_parcelles);


-- qgis_plugin qgis_plugin_pkey
ALTER TABLE ONLY netads.qgis_plugin
    ADD CONSTRAINT qgis_plugin_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--


COMMIT;
