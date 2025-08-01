# ED Data Collecter
A python script that collects data from the EDDN for use in PowerPlay Assistant

Requires:
- Python3
- The zmq pypi package
- The sqalchemy pypi package
- A mariadb database structured as follows:

Systems table: 
`CREATE TABLE IF NOT EXISTS star_systems (system_name VARCHAR(255) PRIMARY KEY, latitude DOUBLE, longitude DOUBLE, height DOUBLE, state VARCHAR(255), shortcode VARCHAR(255), is_anarchy DOUBLE, has_res_sites DOUBLE);`

Megaships table: 
`CREATE TABLE IF NOT EXISTS megaships (name VARCHAR(255) PRIMARY KEY, SYSTEM1 VARCHAR(255), SYSTEM2 VARCHAR(255), SYSTEM3 VARCHAR(255), SYSTEM4 VARCHAR(255), SYSTEM5 VARCHAR(255), SYSTEM6 VARCHAR(255));`

Stations table: 
`CREATE TABLE IF NOT EXISTS stations (id BIGINT PRIMARY KEY AUTO_INCREMENT, station_name VARCHAR(255), star_system VARCHAR(255), station_type VARCHAR(255));`

EXPORT:
SELECT * INTO OUTFILE 'megaships.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '' LINES TERMINATED BY 'NULL' FROM megaships; 