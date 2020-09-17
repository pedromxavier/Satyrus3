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
## Available Solvers

-### Text \[`'text'`\]
Returns the arithmetic expression for the Energy Equation as a Python string.

-### CSV \[`'csv'`\]
Returns a comma-separated values table as a Python string where each line contains a coefficient followed by the respective variable names. There may one line with no variable names, representing a constant term.
