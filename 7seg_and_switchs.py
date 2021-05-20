#!/usr/bin/env python3

from migen import *

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    #leds
    ("user_led", 0, Pins("A8"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("A9"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("A10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("B10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 4, Pins("D13"), IOStandard("3.3-V LVTTL")),
    ("user_led", 5, Pins("C13"), IOStandard("3.3-V LVTTL")),
    ("user_led", 6, Pins("E14"), IOStandard("3.3-V LVTTL")),
    ("user_led", 7, Pins("D14"), IOStandard("3.3-V LVTTL")),
    ("user_led", 8, Pins("A11"), IOStandard("3.3-V LVTTL")),
    ("user_led", 9, Pins("B11"), IOStandard("3.3-V LVTTL")),

    #switchs
    ("user_sw", 0, Pins("C10"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 1, Pins("C11"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 2, Pins("D12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 3, Pins("C12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 4, Pins("A12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 5, Pins("B12"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 6, Pins("A13"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 7, Pins("A14"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 8, Pins("B14"), IOStandard("3.3-V LVTTL")),
    ("user_sw", 9, Pins("F15"), IOStandard("3.3-V LVTTL")),

     # Seven Segment
    ("HEX0", 0, Pins("C14 E15 C15 C16 E16 D17 C17 D15"), IOStandard("3.3-V LVTTL")),
    ("HEX1", 1, Pins("C18 D18 E18 B16 A17 A18 B17 A16"), IOStandard("3.3-V LVTTL")),
    ("HEX2", 2, Pins("B20 A20 B19 A21 B21 C22 B22 A19"), IOStandard("3.3-V LVTTL")),
    ("HEX3", 3, Pins("F21 E22 E21 C19 C20 D19 E17 D22"), IOStandard("3.3-V LVTTL")),
    ("HEX4", 4, Pins("F18 E20 E19 J18 H19 F19 F20 F17"), IOStandard("3.3-V LVTTL")),
    ("HEX5", 5, Pins("J20 K20 L18 N18 M20 N19 N20 L19"), IOStandard("3.3-V LVTTL")),

    ("user_btn", 0, Pins("B8"), IOStandard("3.3-V LVTTL")),

    #clock
    ("clk50", 0, Pins("P11"), IOStandard("3.3-V LVTTL")),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 50e6 #set frequency at 50 MHz

    def __init__(self):
        AlteraPlatform.__init__(self, "10M50DAF484C7G", _io, toolchain="quartus")

# Design -------------------------------------------------------------------------------------------

# Create our platform (fpga interface)
platform = Platform()


# Create our module (fpga description)
class Blink(Module):
    """
    This class create a counter will blink the led at 1 Hz
    blink_freq = blinking frequency
    sys_clk_freq = board frequency
    led = selection of the led
    See the class "Leds_blinks" for more informations
    """
    def __init__(self, blink_freq, sys_clk_freq, led):
        counter = Signal(32)
        # synchronous assignments
        self.sync += [
            counter.eq(counter + 1),
            If(counter == int((sys_clk_freq/blink_freq)/2 - 1),
                counter.eq(0),
                led.eq(~led)
            )
        ]
        # combinatorial assignements
        self.comb += []

class Switch(Module):
    """
    This class associate switchs and leds together
    Leds 0 to 4 will at high state when the switchs are at low state
    Leds 5 to 9 will be inverse due to a not operation on the other leds
    """

    def __init__(self, platform):
        #synchronous assignments
        self.sync += []

        for i in range(0, 5):
            led = platform.request("user_led", i)
            sw = platform.request("user_sw", i)
            self.comb += [led.eq(~sw)]
        for i in range(5, 10):
            led = platform.request("user_led", i)
            sw = platform.request("user_sw", i)
            self.comb += [led.eq(sw)]

class Leds_blinks(Module):
    """
    This class use an other class, so we have to create a submodule
    To do that, write "self.submodules += names_of_functions"
    """
    def __init__(self, platform):
        blink1 = Blink(15, 50e6,platform.request("led1"))
        blink5 = Blink(30, 50e6,platform.request("led5"))
        blink10 = Blink(60, 50e6,platform.request("led10"))
        self.submodules += blink1, blink5, blink10


class hexa(Module):
    """
    This class take the value to display and send it to a 7 segments display
    val = value to display
    seven_seg = 7 segments adress
    """
    def __init__(self, val, seven_seg):
        self.comb += [
            seven_seg.eq(val)
        ]

class affichage(Module):
    """
    This class use hexa class to display value on 7 segments
    The class Switch are call to because If we not call it here, it will be ignore in compilation time
    """
    def __init__(self, platform):
        hex0 = hexa(0b10010010,platform.request("HEX0")) #display 5
        hex1 = hexa(0b10011001,platform.request("HEX1")) #display 4
        hex2 = hexa(0b10110000,platform.request("HEX2")) #display 3
        hex3 = hexa(0b10100100,platform.request("HEX3")) #display 2
        hex4 = hexa(0b11111001,platform.request("HEX4")) #display 1
        hex5 = hexa(0b11000000,platform.request("HEX5")) #display 0
        self.submodules += hex0, hex1, hex2, hex3, hex4, hex5

        sw = Switch(platform)
        self.submodules += sw





#To blink a led at 1Hz :
#module = Blink(1, 50e6, led = platform.request("user_led"))

#To switch on / off leds with swiths : (ps position 0 -> 5 and 5 -> 10 are inverse)
#module = Switch(platform)

#To blink leds 0 5 9 at 1hz 2hz and 4hz
#module = Leds_blinks(platform)

module = affichage(platform)
# Build --------------------------------------------------------------------------------------------

platform.build(module)
