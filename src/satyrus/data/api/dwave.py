from satyrus import SatAPI, Posiform

class dwave(SatAPI):
    """"""

    def solve(self, energy: Posiform, *, num_reads=1_000, num_sweeps=1_000, **params: dict) -> tuple[dict, float]:
        """
        Parameters
        ----------
        energy : Posiform
            Input Expression
        params : dict (optional)
            num_reads : int = 1_000
            num_sweeps : int = 1_000
        """
        import neal

        # Parameter check
        self.check_params(num_reads=num_reads, num_sweeps=num_sweeps)

        self.warn("D-Wave option currently running local simulated annealing since remote connection to quantum host is unavailable")

        self.log(f"Dwave Parameters: num_reads={num_reads}; num_sweeps={num_sweeps}")

        sampler = neal.SimulatedAnnealingSampler()

        x, Q, c = energy.qubo()

        sampleset = sampler.sample_qubo(Q, num_reads=num_reads, num_sweeps=num_sweeps)

        y, e, *_ = sampleset.record[0]

        s = {k: int(y[i]) for k, i in x.items()}

        return (s, e + c)

    def check_params(self, **params: dict):
        if "num_reads" in params:
            num_reads = params["num_reads"]
            if not isinstance(num_reads, int) or num_reads <= 0:
                self.error("Parameter 'num_reads' must be a positive integer")
        else:
            self.error("Missing parameter 'num_reads'")

        if "num_sweeps" in params:
            num_sweeps = params["num_sweeps"]
            if not isinstance(num_sweeps, int) or num_sweeps <= 0:
                self.error("Parameter 'num_sweeps' must be a positive integer")
        else:
            self.error("Missing parameter 'num_sweeps'")