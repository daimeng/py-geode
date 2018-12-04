## Geode
Unfinished WIP
geo toolkit and server

### TODO:
- Caching: DB, Mem
- Rate limits
- User quota
- Retry logic
- More providers: Alk, Bing, etc
- CLI
- Server


### Instructions

pip install git+git://github.com/daimeng/py-geode.git

### Using
```python
from geode.dispatcher import Dispatcher

client = Dispatcher()

res = client.distance_matrix(
    origins=np.array([
        (37.1165, -92.2353),
        (34.1368, -94.5823),
        (37.1165, -92.2353)
    ]),
    destinations=np.array([
        (34.1368, -94.5823),
        (36.3408, -96.0384),
        (32.2834, -92.0286),
        (32.2834, -92.0286)
    ]),
    provider='google') # only google currently
```

returns pandas dataframe:
```
                                          meters       seconds        source
olat    olon     dlat    dlon
34.1368 -94.5823 32.2834 -92.0286  443383.140024  14779.438001  gc_manhattan
                 34.1368 -94.5823       0.000000      0.000000        google
                 36.3408 -96.0384  377076.998820  12569.233294  gc_manhattan
37.1165 -92.2353 32.2834 -92.0286  555963.081690  18532.102723  gc_manhattan
                 34.1368 -94.5823  543109.161164  18103.638705  gc_manhattan
                 36.3408 -96.0384  424897.528514  14163.250950  gc_manhattan
```
