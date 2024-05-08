# qSWIFT

qSWIFT is a Python package that implements a higher-order randomized algorithm for quantum simulation. It is designed to efficiently compute Hamiltonian dynamics with improved error bounds. The algorithm is based on the research presented in the paper: [PRX Quantum 5, 020330](https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.5.020330) (accepted by PRX Quantum).
Please cite the paper, when you utilize this package.

## Installation

We test our code using Python 3.8.5. The package can be installed via pip directly from the GitHub repository. It relies on other packages that are part of the project suite, specifically [qwrapper](https://github.com/konakaji/qwrapper.git) and [benchmark](https://github.com/konakaji/benchmark.git), which are also available on GitHub.

Follow the steps below to install qSWIFT and its dependencies:
```bash
pip install git+ssh://git@github.com/konakaji/qswift.git
```

You can also directly work in this package. In that case, run the following in the project root. 
```bash
pip install -r requirements.txt
```

## Usage

After installation, you can use qSWIFT to simulate quantum systems as per the paper's algorithm. Here's a simple example to get you started 
(you can also check the sample code in https://github.com/konakaji/qswift/blob/master/h.py ):
### Step 1: Prepare Hamiltonian for the time evolution
Prepare the Hamiltonian for the time evolution:

```python
from qwrapper.obs import PauliObservable
from qwrapper.hamiltonian import Hamiltonian
hamiltonian = Hamiltonian([0.2, 0.4], PauliObservable("XX"), PauliObservable("YY"))
```

We can also use the pre-defined Hamiltonian:
```python
from benchmark.molecule import MolecularHamiltonian
hamiltonian = MolecularHamiltonian(8, "6-31g", "hydrogen")
```

### Step 2: Prepare the observable for the expectation value calculation
```python
from qwrapper.obs import PauliObservable
from qwrapper.hamiltonian import Hamiltonian
obs = Hamiltonian([1, 1], [PauliObservable("ZIIIIIII"), PauliObservable("ZZIIIIII")], 8)
```

### Step 3: Prepare the initializer of the quantum circuit
Define the initializer of the quantum circuit:
```python
from qswift.initializer import XBasisInitializer
initializer = XBasisInitializer() # Initialize all qubits in X-basis (other than ancilla qubit).
```

### Step 4: Run qSWIFT
```python
from qswift.qswift import QSwift
qswift = QSwift(obs, initializer, t=t, N=N, K=2, nshot=0, n_p=10000, tool="qulacs")
result = qswift.evaluate(hamiltonian)
```
#### Parameters:
- t: the evolution time
- N: the number of Pauli time evolution gates.
- K: the order parameter
- nshot: # of samples for each circuit generated. When nshot = 0, we use the state vector simulator.
- n_p: # of samples for each order.
- tool: qiskit or qulacs.

### Step 5: Check the result
`result.sum(i)` returns the i-th order calculation result.

```python
print(result.sum(0), result.sum(1), result.sum(2))
```

## Future updates
- We plan to extend the code so that the evolution Hamiltonian can be a sum of arbitrary operators. 
- We plan to add the feature for tuning the number of samples for each order.
