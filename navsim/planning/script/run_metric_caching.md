
### Mini

```
export PYTHONPATH=$PWD:$PYTHONPATH
python navsim/planning/script/run_metric_caching.py train_test_split=mini cache.cache_path=$NAVSIM_EXP_ROOT/metric_cache
```

- ${oc.env:NAVSIM_EXP_ROOT}/metric_cache        