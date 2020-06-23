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
"""
Runs the HPA vs predictive HPA experiment
"""
import os
import sys
import signal
import subprocess
import time
import json

import invokust

from kubernetes import client, config

RUN_TIME = 1800 # 30 mins in seconds
PROBE_INTERVAL = 30 # 30 second probe interval
INTERVAL_OFFSET_BEFORE_LOAD = 5 # wait 5 * 30 seconds (2.5 minutes) as an offset before running the first test
INTERVALS_BEFORE_LOAD = 10 # wait 10 * 30 seconds (5 minutes) interval between running tests

LOCUST_FILE = "./load/load.py"
LOCUST_RUN_TIME = "20s"

def experiment(host, yaml_path, target):
    """
    Runs the chosen YAML for 30 minutes, running regular load tests against it, capturing
    replica counts and latency over time
    """
    print("Creating k8s objects")
    subprocess.run(["kubectl", "apply", "-f", yaml_path], check=True)

    # Wait to let pods start
    time.sleep(30)

    result = {
        "latency": [],
        "replicas": []
    }

    start_time = time.time()
    for i in range(int(RUN_TIME/PROBE_INTERVAL)):
        print("Running probe")
        # Build config in loop as otherwise auth will expire
        config.load_kube_config()
        client_v1 = client.AppsV1Api()

        num_clients = 5
        hatch_rate = 5

        if (i - INTERVAL_OFFSET_BEFORE_LOAD) % INTERVALS_BEFORE_LOAD == 0:
            print("Setting up increased load")
            num_clients = 100
            hatch_rate = 100
        
        locust_settings = invokust.create_settings(
            locustfile=LOCUST_FILE,
            host=f"http://{host}/api/v1/namespaces/default/services/{target}/proxy/",
            num_clients=num_clients,
            hatch_rate=hatch_rate,
            run_time=LOCUST_RUN_TIME
        )
        test = invokust.LocustLoadTest(locust_settings)
        print(f"Running load for {LOCUST_RUN_TIME}")
        test.run()
        print("Finish running load")
        result["latency"].append(test.stats())

        # Log number of replicas
        deployment_resp = client_v1.list_namespaced_deployment(
            "default",
            pretty=True,
            label_selector=f"run={target}")

        replica_count = deployment_resp.items[0].status.replicas
        print("Replicas: ", replica_count)
        result["replicas"].append(replica_count)
        time.sleep(PROBE_INTERVAL - ((time.time() - start_time) % PROBE_INTERVAL))

    print("Deleting K8s objects")
    subprocess.run(["kubectl", "delete", "-f", yaml_path], check=True)

    return result

def main():
    """
    Entrypoint to the experiment
    """
    try:
        host = sys.argv[1]
        results = {}
        results["horizontal"] = experiment(host, "horizontal.yaml", "horizontal-deployment")
        results["predictive"] = experiment(host, "predictive.yaml", "predictive-deployment")

        print("Writing results to results JSON file")
        with open("results/results.json", "w") as file:
            json.dump(results, file)
    except BaseException as err: # pylint: disable=W0703
        print("Unexpected error:", str(err))
        print("Deleting horizontal K8s autoscaler and target")
        subprocess.run(["kubectl", "delete", "-f", "horizontal.yaml"], check=True)

        print("Deleting predictive K8s autoscaler and target")
        subprocess.run(["kubectl", "delete", "-f", "predictive.yaml"], check=True)
        os.killpg(0, signal.SIGKILL)

if __name__ == "__main__":
    main()
