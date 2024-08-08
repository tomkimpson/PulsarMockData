# Pulsar Mock Data


This repo generates frequency timeseries from the [IPTA Mock Data Challenge](https://web.archive.org/web/20130108011819/http://www.ipta4gw.org/?page_id=126). 

See also [https://github.com/nanograv/mdc1](https://github.com/nanograv/mdc1)

The frequency timeseries can then be used as data inputs to state-space filtering algorithms. 



#### Steps


1. Generate "clean" TOAs by passing `.tim` & `.par` files through `tempo2`
2. Add noise (GW, white, red) to clean TOAs to get "perturbed TOAs"
3. Convert "perturbed TOAs" to frequencies which will be ingested by the Kalman filter


A demo of this approach is found in `notebooks/01.explore_how_to_generate_frequencies`.

The script used to generate the actual data used by the Kalman filter is `scripts/generate_frequency_timeseries.py`


#### A note on times 

We are generating an $f(t)$. The method for getting the $f$ part is straightforward, but when should we consider the $t$ to occur?

Two options: `psr.stoas` or `psr.pets`. The difference between the two is << the time interval `dt` so it shouldnt matter too much. 

For `Dataset 1` the data is uniformly sampled. In this case we use `psr.stoas` and assume this `t` is the same for all pulsars. 
