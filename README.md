# Satyrus3

## Install (Windows, Linux, OSx):
```bash
$> git clone https://github.com/pedromxavier/Satyrus3
$> cd Satyrus3
$> pip3 install .
```

## Command Line Interface:
```bash
$> satyrus --help
```

## Example API code:
```python
from satyrus import SatAPI

SOURCE_PATH = r"examples/graph_colour.sat"

## Computes Energy equation
sat = SatAPI(SOURCE_PATH)

## Text output
_, txt = sat['text'].solve()
print(txt)

## CSV output
_, csv = sat['csv'].solve()
with open('sat.csv', 'w') as file:
    file.write(csv)
    
## Gurobi
x, e = sat['gurobi'].solve()

## D-Wave
x, e = sat['dwave'].solve()
```
## Available Solvers

- ### Text \[`'text'`\]
Returns the arithmetic expression (in C/Fortran/Python style) for the energy equation as a Python string.

- ### CSV \[`'csv'`\]
Returns a comma-separated values table as a Python string where each line contains a coefficient followed by the respective variable names. There may one line with no variable names, representing a constant term.

- ### Gurobi \[`'gurobi'`\]
Returns a dictionary mapping variable names to binary value and also the respective total energy.

- ### D-Wave \[`'dwave'`\]
Returns a dictionary mapping variable names to binary value and also the respective total energy. If a connetion to a quantum host is not available, uses `dwave-neal` simulated annealer locally.
