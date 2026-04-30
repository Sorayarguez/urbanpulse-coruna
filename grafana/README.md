# Grafana provisioning and dashboards

This folder contains Grafana provisioning files to register the CrateDB datasource and provision dashboards automatically.

- `provisioning/datasources/cratedb.yaml` — Datasource using the `postgres` driver pointed at CrateDB (port 5432). Set `CRATE_PSQL_USER` and `CRATE_PSQL_PASSWORD` in your environment or Docker Compose.
- `provisioning/dashboards/dashboards.yaml` — Provisioning provider for file-based dashboards.
- `dashboards/*.json` — Exported dashboard JSON files (placeholders). Replace panels with queries for your data model.

To load these locally with Docker Compose, mount this folder into Grafana's provisioning path or copy files into the container's `/etc/grafana/provisioning/` and `/var/lib/grafana/dashboards/` paths.
# Grafana provisioning and dashboards

Placeholders and provisioning for Grafana dashboards used by Issue #6.

- Datasource provisioning: `provisioning/datasources/cratedb.yaml` (Postgres driver pointing to CrateDB on port 5432).
- Dashboard provisioning: `provisioning/dashboards/dashboard.yaml` and JSON files in `dashboards/`.

To load locally with Docker Compose ensure Grafana container mounts `/var/lib/grafana/dashboards` and `/etc/grafana/provisioning` to these files (the project's docker-compose.yml already mounts `grafana-data` volume). Restart Grafana to auto-load the datasources and dashboards.
