On stock ubuntu:

install prometheus and python-prometheus-client

Prometheus GUI (info, status, console): http://localhost:9090


(prometheus-node-exporter gets installed by default)

prometheus-node-exporter exposes some low level metrics - prometheus should scrape from here
http://localhost:9100/metrics

/etc/prometheus/prometheus.yml tells prometheus where to scrape metrics from

install grafana (runs on port 3000)