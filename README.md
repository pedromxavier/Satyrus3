# Satyrus3

## Install:
```$ git clone https://github.com/pedromxavier/Satyrus3
$ python3 setup.py install```

*Note:* The package layout may fail eventually. I advise you to run the platform from the project's folder.

## Example code:
```from satyrus import SatAPI

SOURCE_PATH = r"examples/graph_colour.sat"

sat = SatAPI(SOURCE_PATH)
res = sat['text'].solve()
print(res)```