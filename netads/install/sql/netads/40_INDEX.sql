BEGIN;
--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4 (Debian 15.4-2.pgdg110+1)
-- Dumped by pg_dump version 15.4 (Debian 15.4-2.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

-- parcelles_index_geom_gist
CREATE INDEX parcelles_index_geom_gist ON netads.parcelles USING gist (geom);


-- sidx_communes_geom
CREATE INDEX sidx_communes_geom ON netads.communes USING gist (geom);


-- sidx_geo_impacts_geom
CREATE INDEX sidx_geo_impacts_geom ON netads.geo_impacts USING gist (geom);


--
-- PostgreSQL database dump complete
--


COMMIT;
