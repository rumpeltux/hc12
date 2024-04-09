# HC-12 tools

This was intended as a set of tools that let you modify the HC-12 v2.4 firmware
to run your own code on the onboard STM8S MCU.

However, developing in this environment is tricky, so it’s typically easier to just
use the firmware to extract the radio params and then write your own custom firmware.
Checkout https://github.com/rumpeltux/hc12fw for this.

To avoid any problems with copyright, this repository does not contain the
proprietary firmware image itself, but rather provides tools to extract a
personal backup, so that you can restore the original firmware after
experimenting with your own.

## Why bother?

Writing your own firmware is useful if you

* need different peripheral connections (besides UART)
* have simple sender / receiver logic that can be baked into the MCU
* or want to adjust params of the radio configuration.

## Supported versions

This procedure is currently only known to work with a device that responds with
`www.hc01.com  HC-12_V2.4` to the `AT+VER` command.

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

## Useful references

* [Si4463 Datasheet](https://www.silabs.com/documents/public/data-sheets/Si4464-63-61-60.pdf)
* [STM8S Datasheet](https://www.st.com/resource/en/datasheet/stm8s103f2.pdf)
* Pinout (all partially incomplete, but still helpful).
  * https://twitter.com/cathedrow/status/845044463118553091/photo/1
  * https://cxem.net/review/review26.php
