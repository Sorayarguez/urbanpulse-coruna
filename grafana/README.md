# Grafana provisioning and dashboards

Placeholders and provisioning for Grafana dashboards used by Issue #6.

- Datasource provisioning: `provisioning/datasources/cratedb.yaml` (Postgres driver pointing to CrateDB on port 5432).
- Dashboard provisioning: `provisioning/dashboards/dashboard.yaml` and JSON files in `dashboards/`.

To load locally with Docker Compose ensure Grafana container mounts `/var/lib/grafana/dashboards` and `/etc/grafana/provisioning` to these files (the project's docker-compose.yml already mounts `grafana-data` volume). Restart Grafana to auto-load the datasources and dashboards.
