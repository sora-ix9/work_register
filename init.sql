CREATE DATABASE work_register_db;

\c work_register_db;

CREATE TABLE work_register_tb (
    registry_id SERIAL PRIMARY KEY,
    officer_id VARCHAR (255),
    full_name VARCHAR (255),
    registry_img BYTEA,
    registry_time VARCHAR (255)
);