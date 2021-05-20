#!/usr/bin/env python3

from migen import *

# Design -----------------------------------

class Counter(Module):
    """
    Test on a simple counter
    On rising edge of the clock the counter increment
    Use of the overflow to reset and count again
    """

    def __init__(self):
        counter = Signal(8) #counter is a 8 bit Signal

        self.sync += [counter.eq(counter + 1)]

module = Counter()

# Main -----------------------------------

if __name__ == '__main__':
    dut = Counter()

    def dut_tb(dut):
        for i in range(512):
            yield

    run_simulation(dut, dut_tb(dut), vcd_name="counter.vcd")
