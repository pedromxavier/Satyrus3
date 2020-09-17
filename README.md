# Satyrus3

## Install:
```bash
$ git clone https://github.com/pedromxavier/Satyrus3
$ python3 setup.py install
```

*Note:* The package loading may fail eventually. I advise you to run the platform from the project's folder until this is fixed.

## Example code:
```python
from satyrus import SatAPI

SOURCE_PATH = r"examples/graph_colour.sat"

## Text output
sat = SatAPI(SOURCE_PATH)
txt = sat['text'].solve()
print(txt)

## CSV output
csv = sat['csv'].solve()
with open('sat.csv', 'w') as file:
    file.write(csv)
```
