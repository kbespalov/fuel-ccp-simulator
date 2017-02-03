import yaml
import json
import os
import logging
import argparse
import sys

from influxdb import InfluxDBClient

# configuration
CONF = None

# logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
log.debug('start')


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='filename', default=None, type=str,
                        help='Path to the json file with simulator metrics')
    parser.add_argument('-t', dest='tag', default=None, type=str,
                        help='InfluxDB serias tag')
    parsed = parser.parse_args(sys.argv[1:])
    CONF['filename'] = parsed.filename
    CONF['tag'] = parsed.tag


def load_config(path='/messaging/collector.yaml'):
    """Load a configuration from file and parse args"""
    global CONF
    with open(path) as f:
        CONF = yaml.load(f)
    parse_args()


def get_servers_stats():
    """Load the rpc server's result series from output directory"""

    stats_dir = CONF['stats_dir']
    files = [CONF['filename']] if CONF['filename'] else os.listdir(stats_dir)

    for filename in files:
        if not filename.startswith('server'):
            continue
        with open(os.path.join(stats_dir, filename)) as fd:
            yield filename, json.load(fd)


def measurement_body(server, topic, data):
    """Create json-based influxdb measurement point"""
    return {
        "measurement": "simulator",
        "tags": {"server": server, "topic": topic, "tag": CONF['tag']},
        "time": int(data["timestamp"]) * 10 ** 9,
        "fields": {
            "latency": data["latency"],
            "count": data["count"],
            "size": data["size"]
        }}


def get_influxdb_client():
    """Initialize the instance of influxdb client and create database"""
    client = InfluxDBClient(**CONF['influxdb'])
    client.create_database(CONF['influxdb']['database'])
    return client


def main():
    client = get_influxdb_client()
    for filename, stat in get_servers_stats():
        parsed = filename.split('.')[0].split('_')  # server_0_1.json
        server, topic = parsed[1], parsed[2]
        log.debug('Collect statistics: server %s topic %s ' % (server, topic))
        series = stat['series']['server']
        batch = []
        for s in series:
            if s["count"]:
                batch.append(measurement_body(server, topic, s))
        client.write_points(batch)


if __name__ == '__main__':
    load_config()
    main()
