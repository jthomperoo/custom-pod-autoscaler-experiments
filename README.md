# Custom Pod Autoscaler Experiments

This repo holds a number of experiments and reports, comparing the Custom Pod Autoscaler (and it's implemenetations) to existing scaling solutions.

## Experiments

* [**Game Server Scaling**](game-server-scaling/) - Comparing Custom Pod Autoscaler with [Agones fleet autoscaler](https://github.com/googleforgames/agones).
* [**Horizontal Pod Autoscaler**](horizontal-pod-autoscaler/) - Comparing Custom Pod Autoscaler reimplementation of Horizontal Pod Autoscaler with the existing Horziontal Pod Autoscaler.
* [**Locust Pod Autoscaler**](locust-pod-autoscaler/) - Comparing Locust Pod Autoscaler (built with Custom Pod Autoscaler) and existing Horizontal Pod Autoscaler solution for scaling based on latency and load testing results.
* [**Predictive Horizontal Pod Autoscaler**](predictive-horizontal-pod-autoscaler/) - Comparing Predictive Horizontal Pod Autoscaler against existing Horizontal Pod Autoscaler for regular loads, comparisons between latency and request failures.
* [**Scale On Tweet**](scale-on-tweet/) - Comparing a Custom Pod Autoscaler implementation of scaling based on number of tweets with a hashtag and expected value and how it would have to be implemented without the Custom Pod Autoscaler.

## Report

### Dependencies

Generating the report PDF requires:

* [`pandoc`](https://pandoc.org/installing.html)
* `make` - ([Windows installation](http://gnuwin32.sourceforge.net/packages/make.htm))

### Generating

To generate the report, run

```
make
```

The report will be output to `disseration.pdf`.