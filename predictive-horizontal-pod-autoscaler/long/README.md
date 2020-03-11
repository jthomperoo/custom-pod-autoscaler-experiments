# Long Term Predictive vs Standard Horizontal Pod Autoscaler

This experiment is designed to compare the Predictive Horizontal Pod Autoscaler (PHPA) with the Standard Kubernetes Horizontal Pod Autoscaler (HPA) for autoscaling based on regular, seasonal loads; over a long period (in this case a week).  

## Hypothesis

The Predictive Horizontal Pod Autoscaler using the Holt-Winters prediction method will pre-emptively scale, reacting earlier than the standard Kubernetes Horizontal Pod Autoscaler. This will be manifested in higher replica counts when scaling up, and scaling up earlier; with the result of lower average and maximum latency, and less failed requests - primarily around the moment of change from lower load levels to high load. This effect will only be apparant however after at least one full season (24 hours); for the first season as the predictor won't have data to make a prediction it will be largely the same performance as the standard Kubernetes Horizontal Pod Autoscaler.

## Experiment

This experiment will run for a week - 7 days - and is designed to have the PHPA and HPA running in their own clusters. Everything should be kept the same between the two autoscalers - they will both manage the same application, and the load will be managed by the same load testing logic.  

Each test will have have three elements, the autoscaler, an application to manage, and the load testing applications. The autoscaler will be the only part that changes. The application will be a simple example web server that responds `OK!` to `GET` at path `/`; it is the `k8s.gcr.io/hpa-example` that is used in Kubernetes autoscaling walkthroughs. The load testing application will be a python script that will invoke Locust load testing at set intervals, varying the load applied based on the time of day. The load testing will also periodically record how many replicas the deployment has.  

See these diagrams for overviews of the test:

![Predictive Horizontal Pod Autoscaler Experiment](diagrams/PHPA_long_experiment_phpa_design.svg)  
**Predictive Horizontal Pod Autoscaler Experiment**

![K8s Horizontal Pod Autoscaler Experiment](diagrams/PHPA_long_experiment_k8s_hpa_design.svg)  
**K8s Horizontal Pod Autoscaler Experiment**

The load applied will be the same for each autoscaler;
- High load (300 users) will be applied between 15:00 and 17:00.
- Medium load (150 users) will be applied between 9:00 and 12:00.
- Low load (75 users) will be applied for all other times.

The Horizontal Pod Autoscaler will be configured with the following options:
- Minimum replicas: `1`.
- Maximum replicas: `20`.
- Sync Period (`--horizontal-pod-autoscaler-sync-period`): `15s` (default).
- Downscale Stabilization (`--horizontal-pod-autoscaler-downscale-stabilization`): `5m` (default).
- Tolerance (`--horizontal-pod-autoscaler-tolerance`): `0.1` (default).
- CPU Initialization Period (`--horizontal-pod-autoscaler-cpu-initialization-period`): `5m` (default).
- Initial Readiness Delay (`--horizontal-pod-autoscaler-initial-readiness-delay`): `30s` (default).
- Metrics: Resource metric targeting CPU usage, with average utilization at `50`.

The Predictive Horizontal Pod Autoscaler will have the same settings as the Horizontal Pod Autoscaler:
- Minimum replicas: `1`.
- Maximum replicas: `20`.
- Sync Period (`--horizontal-pod-autoscaler-sync-period`): `15` (equivalent to `15s`) (default).
- Downscale Stabilization (`--horizontal-pod-autoscaler-downscale-stabilization`): `300` (equivalent to `5m`) (default).
- Tolerance (`--horizontal-pod-autoscaler-tolerance`): `0.1` (default).
- CPU Initialization Period (`--horizontal-pod-autoscaler-cpu-initialization-period`): `300` (equivalent to `5m`) (default).
- Initial Readiness Delay (`--horizontal-pod-autoscaler-initial-readiness-delay`): `30` (equivalent to `30s`) (default).
- Metrics: Resource metric targeting CPU usage, with average utilization at `50`.

The Predictive Horizontal Pod Autoscaler will also have the following configuration settings for tuning the Holt-Winters algorithm:
- Model Holt-Winters
  * Per Interval: `1` (Run every interval)
  * Alpha: `0.9`
  * Beta: `0.9`
  * Gamma: `0.9`
  * Season Length: `288` (24 hours in 5 minute intervals)
  * Stored Seasons: `4` (store last 4 days data)
  * Method: `additive`

## Results

## Conclusion

## Running the experiment

### Environment

Running this experiment will require a Kubernetes cluster than can support ~25 pods, with the metrics server enabled.  
The experiment requires the Custom Pod Autoscaler Operator installed on the cluster, which can be installed [by following this guide](https://github.com/jthomperoo/custom-pod-autoscaler-operator/blob/master/INSTALL.md).  

### Load testing application

Each test will need access to the load testing application, which must be built and pushed to a registry that the cluster has access to.  
To build the load testing application:
```
docker build -t YOUR_REGISTRY/load-test:latest load
```
To push the application to your registry:
```
docker push YOUR_REGISTRY/load-test:latest
```
Finally you must update the `hpa.yaml` and `phpa.yaml` files, with any reference to the `load-test:latest` image changed to `YOUR_REGISTRY/load-test:latest`.

### Running

Once the cluster has been set up, the PHPA test can be run by simply applying the `phpa.yaml` to the cluster with:
```
kubectl apply -f phpa.yaml
```

The HPA test can be run similarly through `hpa.yaml`:
```
kubectl apply -f hpa.yaml
```

These should be left to run for a period of time and preferably not on the same cluster at the same time.

### Retrieving results

The results will be stored in the `load-test` container, in the `/results` folder, there are two CSV files:
- `load.csv` - data around the load testing, in the following structure:
```csv
timestamp,num_requests,num_requests_fail,avg_response_time,min_response_time,max_response_time
```
- `replicas.csv` - data of the number of replicas over time, in the following structure:
```csv
timestamp,num_replicas
```