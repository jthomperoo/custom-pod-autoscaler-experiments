# Long Term Predictive vs Standard Horizontal Pod Autoscaler

This experiment is designed to compare the Predictive Horizontal Pod Autoscaler (PHPA) with the Standard Kubernetes Horizontal Pod Autoscaler (HPA) for autoscaling based on regular, seasonal loads; over a long period (in this case a week).  

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