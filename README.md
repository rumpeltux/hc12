# HC-12 tools

This was intended as a set of tools that let you modify the HC-12 v2.4 firmware
to run your own code on the onboard STM8S MCU.

However, developing in this environment is tricky, so it’s typically easier to just
use the firmware to extract the radio params and then write your own custom firmware.

To avoid any problems with copyright, this repository does not contain the firmware
image itself, but rather provides tools to extract a personal backup, so that you
can restore the original firmware after experimenting with your own.

## Why bother?

Writing your own firmware is useful if you

* need different peripheral connections (besides UART)
* have simple sender / receiver logic that can be baked into the MCU
* or want to adjust params of the radio configuration.

## Process

To make a backup of your firmware, follow these steps:

* Use a USB-to-serial converter, and connect the HC-12 according to the official pinout.
* VCC can be anything from 3.3 to 5.5V.
* Make sure that the SET pin is connected to GND.

Run the firmware extraction tool:

    ./firmwaredump -d /dev/ttyUSB0 -f hc12-fw.bin

The tool overwrites the `AT+VER` command handler by flashing a short segment of code.
`AT+VER` then dumps the original firmware (except for the original AT+VER handler,
but you should be able to guess its contents).

## Restoring the chip

If your custom software messes up the chip’s functionality, you can always restore
(almost) the original firmware. You’ll need a programmer (an stlink or an esp8266 with
[espstlink](https://github.com/rumpeltux/esp-stlink)).

You can then reflash the firmware using `stm8flash`. First you need to
disable both readout protection and write protected pages, which will erase flash and eeprom.

    echo "00 00 ff 00 ff 00 ff 00 ff 00 ff" | xxd -r -p > factory_defaults.bin
    stm8flash -c espstlink -p stm8s103f3 -s opt -w factory_defaults.bin

We also need a little patch to the firmware (it sets up the actual entry point in eeprom on first run):

    echo "02: 8590" | xxd -r - hc12-fw.bin

Now we can flash it and the chip should work as it did before:

    stm8flash -c espstlink -p stm8s103f3 -w hc12-fw.bin

## Writing software

I experimented briefly with hijacking unused code regions to run my own code,
but this turned out not to be worth the trouble. Some of the caveats:

* don't use more than 177 bytes of RAM (also: it's not really tested if the designated ram section is really unused…)
* code size is quite limited, but there should be up to 1k of usable space.
  You may have to designate code into separate areas though.
  For that use the `#pragma codeseg NAME` directive.

Most importantly: any custom code will run closely intertwined with the existing
firmware. It's easily possible to mess up and render the chip unusable.
In that case refer to *Restoring the chip* on how to factory reset it.

stm8flash also doesn’t deal well with partial binary patches as provided in the
ihx output of the build process.

### Non-essential code areas

| size| start| end  | original function                            | Segment name
|-----|------|------|----------------------------------------------|--------------
| 236 | 8121 | 820D | AT+FU5                                       | CODE1
| 254 | 8E4F | 8F4C |                                              | **DATA**
| *129|  8E4F|  8ED0|  AT+FU5                                      | 
| *124|  8ED0|  8F4C|  AT+FU6                                      | 
| 492 | 875F | 894B | readBaud, readChannel, readFU, readTXPower   | **CODE**
| 217 | 8AF8 | 8BD1 | printVersion                                 | CODE2
| 189 | 9882 | 993F | AT+FU4                                       | STDLIB1

**Bold** designates default areas. You can override the destination per `.c` file
using the `#pragma codeseg NAME` directive (or `dataseg` for const data).

### Available GPIO PINs

The following STM8 PINs are available for you to use:
A1,A2,A3\* D1\*,D3,D4\*

* A3: signaling chip boot readiness
* D1: SWIM used for programming (already has testport solder pad)
* D4: used as output toggles on radio TX?

If you just need one extra PIN, D3 is probably a good choice, since its leg
is easily accessible at the chip edge for soldering.

## Useful references

* [Si4463 Datasheet](https://www.silabs.com/documents/public/data-sheets/Si4464-63-61-60.pdf)
* [STM8S Datasheet](https://www.st.com/resource/en/datasheet/stm8s103f2.pdf)
* Pinout (all partially incomplete, but still helpful).
  * https://twitter.com/cathedrow/status/845044463118553091/photo/1
  * https://cxem.net/review/review26.php
