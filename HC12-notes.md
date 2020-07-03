# Prior work

Brain transplant: https://github.com/al177/hc12pj
(completely new firmware)

Pinout (somewhat incomplete as it looks):
https://twitter.com/cathedrow/status/845044463118553091/photo/1

# Undocumented Commands
AT+FS
AT+FT
AT+FDR
AT+I
AT+FU4
AT+FU5 (FS)
AT+FU6 (FT demo mode sends 'How are you' 'Long time no see' via UART)
AT+FU7 (FDR)

'Dabcde....'
Send a bytes from address cd as SPI command
Receive b bytes to address de via SPI

'\xDEab' set demo delay (a * b * 10us)
'\xEE'

# Update procedure

AT+UPDATE
wait .1s (unclear why this works, because there doesn't seem to be a path to the update_handler w/o sending 0xEE, maybe WD reset?)
switch to 19200 baud
send 'I'

package contains at most 0x25 bytes
[0] = length 
[1] = 0
[2] = update location high
[3] = update location low
[4..0x23] = update data
[0x24] = checksum (0x100 - uint8_t (sum [0..0x24]))

Update location must be >= 0x8000 and <= 0x9A00 and on a 32 byte boundary
Length must not be 15.

The reset vector (0x8000 to 0x8003) cannot be overwritten.

## Remove Update procedure

pinSET pullup, wait a bit until regular FU3 is setup
pinSET down, up, down. Should cause a reset to enter OTA update mode.

Send P + 0x24 bytes update package.

## Non-essential code locations
236 8121 820D AT+FU5                                       CODE1
254 8E4F 8F4C                                              DATA
  129 8E4F 8ED0 AT+FU5 
  124 8ED0 8F4C AT+FU6
492 875F 894B readBaud, readChannel, readFU, readTXPower   CODE
217 8AF8 8BD1 printVersion                                 CODE2
189 9882 993F AT+FU4                                       STDLIB1
sum: 1.4k

--code-loc 875F

location for packet_recv_handler:
104 93D4 943C uart_tx

## Pinout

https://cxem.net/review/review26.php
https://twitter.com/cathedrow/status/845044463118553091/photo/1

D4
D5     TX
D6     RX
A1,2   osc
A3     module ready signal

D3
D2           NSEL
D1  SWIM
C7           MISO
C6           MOSI
C5           SCLK
C4            IRQ
C3             01
B4        GPIO 00
B5            SET

Available: A1,2,3* D1*,3,4*
A3 signaling chip boot readiness
D1 SWIM used for programming
D4 used as output toggles on TX
D3

## RFIC Programming Guide
http://www.farnell.com/datasheets/1889753.pdf
0x02 POWER_UP Command to power-up the device and select the operational
mode and functionality.
COMMON_COMMANDS
0x00 NOP No operation command.
0x01 PART_INFO Reports basic information about the device.
0x10 FUNC_INFO Returns the Function revision information of the device.
0x11 SET_PROPERTY Sets the value of one or more properties.
0x12 GET_PROPERTY Retrieves the value of one or more properties.
0x13 GPIO_PIN_CFG Configures the GPIO pins.
0x15 FIFO_INFO Access the current byte counts in the TX and RX FIFOs and provide for resetting the FIFOs.
0x20 GET_INT_STATUS Returns the interrupt status of ALL the possible interrupt events
(both STATUS and PENDING). Optionally, it may be used to
clear latched (PENDING) interrupt events.
0x33 REQUEST_DEVICE_STATE Request current device state and channel.
0x34 CHANGE_STATE Manually switch the chip to a desired operating state.
0x38 OFFLINE_RECAL Recalibrates due to temperature change.
0x44 READ_CMD_BUFF Used to read CTS and the command response.
0x50 FRR_A_READ Reads the fast response registers (FRR) starting with FRR_A.
0x51 FRR_B_READ Reads the fast response registers (FRR) starting with FRR_B.
0x53 FRR_C_READ Reads the fast response registers (FRR) starting with FRR_C.
0x57 FRR_D_READ Reads the fast response registers (FRR) starting with FRR_D.
0x17 IRCAL Image rejection calibration.
0x19 IRCAL_MANUAL Image rejection calibration.
TX_COMMANDS
0x31 START_TX Switches to TX state and starts transmission of a packet.
0x37 TX_HOP Hop to a new frequency while in TX.
0x66 WRITE_TX_FIFO Writes data byte(s) to the TX FIFO.
RX_COMMANDS
0x16 PACKET_INFO Returns information about the length of the variable field in the
last packet received and (optionally) overrides field length.
0x22 GET_MODEM_STATUS Returns the interrupt status of the Modem Interrupt Group (both
STATUS and PENDING). Optionally, it may be used to clear
latched (PENDING) interrupt events.
0x32 START_RX Switches to RX state and starts reception of a packet.
0x36 RX_HOP Manually hop to a new frequency while in RX mode.
0x77 READ_RX_FIFO Reads data byte(s) from the RX FIFO.
ADVANCED_COMMANDS
0x14 GET_ADC_READING Performs conversions using the Auxiliary ADC and returns the
results of those conversions.
0x21 GET_PH_STATUS Returns the interrupt status of the Packet Handler Interrupt
Group (both STATUS and PENDING). Optionally, it may be
used to clear latched (PENDING) interrupt events.
0x23 GET_CHIP_STATUS Returns the interrupt status of the Chip Interrupt Group (both
STATUS and PENDING). Optionally, it may be used to clear
latched (PENDING) interrupt events.

