# fuel-ccp-simulator
CCP deployment of oslo.messaging simulator

* example of ccp topology:  [topology.yaml](topology_example.yaml) 
* grafana dashboard to display metrics results: [grafana_dashborad.json](service/files/grafana_dashborad.json)

How its works ?

1. As soon as a rpc server has been process all recieved messages it dump statistics to the json file:
`/var/log/ccp/simulator/server_{server_id}_{topic_id}.json`
2. Then the statistic collector script [collector.py](service/files/collector.py) push the data to influxdb:

  ```
  database: simulator

  "measurement": "simulator",
  "tags": {"server": server_id, "topic": topic_id, "tag": CONF['tag']},
  "time": int(data["timestamp"]) * 10 ** 9,
      "fields": {
          "latency": data["latency"],
          "count": data["count"],
          "size": data["size"]
  ```

  To distinguish the data in database, you can specify a tag in confgs section of `topology.yaml`:
  
  ```
  configs:
  simulator:
    influxdb_tag: simulator_run_3_topics_2_servers_zmq_backend
  ```
   
3. The first step to show results in the Grafana is configuration the datasource in dashboard:

   ![alt tag](https://image.ibb.co/fgKK5a/2017_02_03_16_06_32.png)

   Then you must to import the dashboard from file [grafana_dashborad.json](service/files/grafana_dashborad.json)
   and show results:
   
   ![alt tag](https://image.ibb.co/eyBMJv/2017_02_03_16_10_42.png)
   
