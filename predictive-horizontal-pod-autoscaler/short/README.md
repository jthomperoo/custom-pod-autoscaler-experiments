# CPA Predictive Horizontal Pod Autoscaler vs K8s Horizontal Pod Autoscaler

This experiment compares the performance of the CPA Predictive Horizontal Pod Autoscaler and the K8s Horizontal Pod Autoscaler for regular, seasonal loads.  

The experiment runs a sample application, and uses the autoscalers to monitor it; every 5 minutes an increased load is used, which should cause the autoscalers to react to this. The experiment runs these increased loads 6 times, meaning the experiment runs for 30 minutes per autoscaler.  

## Running the experiment

### Environment

Running this experiment requires a Kubernetes cluster, which you are authenticated with, that is set up with the following:

* K8s downscale stabilization flag needs set; `--horizontal-pod-autoscaler-downscale-stabilization=0s`.
* The [Custom Pod Autoscaler Operator](https://github.com/jthomperoo/custom-pod-autoscaler-operator) needs to be installed, follow [the guide here](https://github.com/jthomperoo/custom-pod-autoscaler-operator/blob/master/INSTALL.md).

Running the experiment locally will also require:

* `python >= 3.7.4`

To install the pip dependencies use:

```
python -m pip install -r requirements.txt
```

### Set up the Kubectl proxy

This experiment requires a kubectl proxy before it can run, which can be set up
with the following command:

```
kubectl proxy
```

### Running the script

The experiment is run by using the following command:

```
python experiment.py 127.0.0.1:8001
```

Replace `127.0.0.1:8001` with whichever host:port combination your proxy is set
up with.

Once the experiment is complete the results are collected and written to `results/results.json`.

## Analysing the experiment

The results of the experiment can be analysed and graphs generated using the following command:

```
python analyse.py
```

This will result in some SVG graphs and a markdown table output to `results/`.
