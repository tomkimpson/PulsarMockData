# Pulsar Mock Data


This repo generates frequency timeseries from the [IPTA Mock Data Challenge](https://web.archive.org/web/20130108011819/http://www.ipta4gw.org/?page_id=126). See also [https://github.com/nanograv/mdc1](https://github.com/nanograv/mdc1)

The frequency timeseries can then be used as data inputs to state-space filtering algorithms. 



#### Steps


1. Generate "clean" TOAs by passing `.tim` & `.par` files through `tempo2`
2. Add noise (GW, white, red) to clean TOAs to get "perturbed TOAs"
3. Convert "perturbed TOAs" to frequencies which whill be ingested by the Kalman filter
