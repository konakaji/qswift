from qswift.initializer import CircuitInitializer
from scipy.linalg import expm
import numpy as np
import torch 



class Channel:
    def __init__(self, m, inv, device="cpu"):
        self.device = device
        if self.device == "cpu":
            self.m = np.array(m)
            self.inv = np.array(inv)
        elif self.device == "gpu":
            self.m = torch.tensor(m, device='cuda')
            self.inv = torch.tensor(inv, device='cuda')

    def apply(self, rho):
        if self.device == "cpu":
            return self.m.dot(rho).dot(self.inv)
        elif self.device == "gpu":
            rho = torch.tensor(rho, device='cuda')
            result = torch.matmul(torch.matmul(self.m, rho), self.inv)
            return result.cpu().numpy()  # Convert back to numpy array if needed




class ExactComputation:
    def __init__(self, obs, hamiltonian_matrix, t, initializer: CircuitInitializer, device='cpu'):
        self.device = device
        self.initializer = initializer
        if self.device == 'cpu':
            self.hamiltonian_matrix = np.array(hamiltonian_matrix)
        elif self.device == 'gpu':
            self.hamiltonian_matrix = torch.tensor(hamiltonian_matrix, dtype=torch.complex64, device='cuda')
        self.t = t
        if self.device == 'cpu':
            self.obs = np.array(obs)
        elif self.device == 'gpu':
            self.obs = torch.tensor(obs, dtype=torch.complex64, device='cuda')

    def compute(self):
        if self.device == 'cpu':
            channel = Channel(expm(1j * self.hamiltonian_matrix * self.t), expm(-1j * self.hamiltonian_matrix * self.t), device='cpu')
            state = self.initializer.initial_state(len(self.hamiltonian_matrix))
            rho = channel.apply(state)
            return np.trace(rho.dot(self.obs)).real
        elif self.device == 'gpu':
            channel = Channel(expm(1j * self.hamiltonian_matrix.cpu().numpy() * self.t), expm(-1j * self.hamiltonian_matrix.cpu().numpy() * self.t), device='gpu')
            state = torch.tensor(self.initializer.initial_state(len(self.hamiltonian_matrix)), dtype=torch.complex64, device='cuda')
            rho = channel.apply(state)
            trace_result = torch.trace(torch.matmul(rho, self.obs))
            return trace_result.real.cpu().item()

