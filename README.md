# Satyrus3

`$ python3 setup.py install`
```
from satyrus import SatAPI

SOURCE_PATH = r"examples/graph_colour.sat"

sat = SatAPI(SOURCE_PATH)
res = sat['text'].solve()
print(res)
```