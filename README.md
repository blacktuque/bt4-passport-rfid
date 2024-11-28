# BT4 Passport RFID Tag Writer

## Set Up

### Install Dependencies

```
python3 -m venv venv
source venv/bin/activate
pip install ./passport-0.1.0-cp37-abi3-manylinux_2_34_x86_64.whl
pip install -r requirements.txt
```

## Hardware

You will need a PN532 breakout board and a serial to usb interface. 

- https://www.amazon.ca/dp/B00KKUECAO
- https://www.amazon.ca/dp/B09WMDBKP4

If you get a cheap one like this (https://www.amazon.ca/dp/B07YFX5X9Y) it should work for writing tags, but it definitely will not work to simulate the ATM active/active connection.

You will also need NTAG215 or NTAG216 tags. Example here: 
- https://www.amazon.ca/dp/B0CPJ5DDCQ

You can overwrite the tags you already have as well.

## Set up your PN532

Get the vendor and product id from dmesg when you plug it in. If it's differnet than below, edit the params before writing the file.

This step ensures that the device has the appropriate permissions to access the device as a non-root user.

```
sudo echo 'SUBSYSTEMS=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", MODE="0666"' > /etc/udev/rules.d/99-usbftdi.rules
```

## Running

### Writing RFID Tags

```
python3 tag-write.py
```

### Simulating the ATM and calculating score

```
python3 atm.py
```
