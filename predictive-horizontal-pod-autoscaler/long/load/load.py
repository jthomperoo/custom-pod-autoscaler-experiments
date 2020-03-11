# Copyright 2020 Jamie Thompson.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import signal
import time
import invokust
import asyncio
from datetime import datetime
from threading import Thread
from kubernetes import client, config

LABEL_SELECTOR = "run=experiment-deployment"
NAMESPACE = "default"

REPLICAS_FILE = "/results/replicas.csv"
LOAD_RESULTS_FILE = "/results/load.csv"

HOST = "http://experiment-deployment.default.svc.cluster.local"
LOCUST_FILE = "/locust/locust.py"

RUN_TIME = "5m"
MONITOR_INTERVAL = 15

LOW_NUM_CLIENTS = 15
LOW_HATCH_RATE = 3

MEDIUM_NUM_CLIENTS = 40
MEDIUM_HATCH_RATE = 4

HIGH_NUM_CLIENTS = 80
HIGH_HATCH_RATE = 20

MEDIUM_LOAD = (9, 12)
HIGH_LOAD = (15, 17)

class TimeRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end

class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True


def load():
    killer = GracefulKiller()
    while not killer.kill_now:
        print("Running load")
        now = datetime.utcnow()
        print("Current time:", now.strftime("%H:%M"))

        num_clients = LOW_NUM_CLIENTS
        hatch_rate = LOW_HATCH_RATE

        if MEDIUM_LOAD[0] <= now.hour < MEDIUM_LOAD[1]:
            print(f"Hour between {MEDIUM_LOAD[0]} and {MEDIUM_LOAD[1]}, running medium load")
            num_clients = MEDIUM_NUM_CLIENTS
            hatch_rate = MEDIUM_HATCH_RATE
        elif HIGH_LOAD[0] <= now.hour < HIGH_LOAD[1]:
            print(f"Hour between {HIGH_LOAD[0]} and {HIGH_LOAD[1]}, running high load")
            num_clients = HIGH_NUM_CLIENTS
            hatch_rate = HIGH_HATCH_RATE
        else:
            print(f"Running low load")
        
        settings = invokust.create_settings(
            locustfile=LOCUST_FILE,
            host=HOST,
            num_clients=num_clients,
            hatch_rate=hatch_rate,
            run_time=RUN_TIME
        )

        load_test = invokust.LocustLoadTest(settings)
        load_test.run()
        results = load_test.stats()

        requests = results.get("requests")
        request = requests.get("GET_/")
        avg_response_time = request.get("avg_response_time")
        min_response_time = request.get("min_response_time")
        max_response_time = request.get("max_response_time")

        num_requests = results.get("num_requests")
        num_requests_fail = results.get("num_requests_fail")

        timestamp = now.timestamp()

        with open(LOAD_RESULTS_FILE, "a") as file:
            file.write(f"{timestamp},{num_requests},{num_requests_fail},{avg_response_time},{min_response_time},{max_response_time}\n")
    print("Shutting down...")

def monitor():
    killer = GracefulKiller()
    while not killer.kill_now:
        now = datetime.utcnow()
        timestamp = now.timestamp()

        config.load_incluster_config()
        client_v1 = client.AppsV1Api()
        deployment_resp = client_v1.list_namespaced_deployment(
            NAMESPACE,
            pretty=True,
            label_selector=LABEL_SELECTOR)

        replica_count = deployment_resp.items[0].status.replicas
        with open(REPLICAS_FILE, "a") as file:
            file.write(f"{timestamp},{replica_count}\n")
        time.sleep(MONITOR_INTERVAL)

if __name__ == "__main__":
    Thread(target = load).start()
    Thread(target = monitor).start()
