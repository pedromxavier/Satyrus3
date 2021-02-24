# Satyrus3

## Install
Requires 3.7+ CPython ([python.org](https://www.python.org)) distribution.
- ### Linux, OSx
    ```bash
    $ git clone https://github.com/pedromxavier/Satyrus3
    $ cd Satyrus3
    $ pip3 install .
    ```
- ### Windows:
    ```shell
    > git clone https://github.com/pedromxavier/Satyrus3
    > cd Satyrus3
    > pip install .
    ```

## Command line interface:
```bash
$ satyrus --help
$ satyrus examples/graph_colour.sat > graph_colour.txt
$ satyrus examples/graph_colour.sat -o csv > graph_colour.csv
```

## Example API code:
```python
from satyrus import SatAPI

SOURCE_PATH = r"examples/graph_colour.sat"

## Computes Energy equation
sat = SatAPI(SOURCE_PATH)

## Text output
txt = sat['text'].solve()
print(txt)

## CSV output
csv = sat['csv'].solve()
with open('sat.csv', 'w') as file:
    file.write(csv)
    
## Gurobi
x, e = sat['gurobi'].solve()

## D-Wave
x, e = sat['dwave'].solve()
```
## Available solver interfaces

### Partial
These solvers output either problem specifications or intermediate data.
- ### Text \[`'text'`\]: <br> Returns the arithmetic expression (in C/Fortran/Python style) for the energy equation as a Python string.

- ### CSV \[`'csv'`\] <br> Returns a comma-separated values table as a Python string where each line contains a coefficient followed by the respective variable names. A single line with no variable names, represents a constant term.

### Complete
Complete ones output a dictionary (Python `dict`) mapping variable names to binary value and also the respective total energy (Python `float`).

- ### Gurobi \[`'gurobi'`\] <br> May require license for usage.

- ### D-Wave \[`'dwave'`\] <br> If a connetion to a quantum host is not available, runs `dwave-neal` simulated annealer locally.
