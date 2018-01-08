WARNING - __this is presently undergoing beta testing__  - I will remove this warning once more people have tested it out.

bip38-pi-airgap
===============
A script-assisted process for setting up a minimal Raspberry Pi OS image for decrypting BIP38 private keys and using Electrum. It is designed and intended to be used on an airgapped setup to limit exposure of private keys to external devices and networks.

This is intended to be a high-security process, so __please check the filed Issues section for any known issues before proceeding__ and also please file issues if there are any discovered concerns.

This may also be helpful for setting up an airgapped system to use Electrum with non-BIP38 keys via the `importprivkey` command. However, this process includes installing dependency packages specifically for the BIP38 cryptography which is not necessary if there is no intention of doing BIP38 decryption. This process may also be useful as part of a platform for generating private keys and addresses in an airgapped environment, however __ensuring sufficient random entropy on the Raspberry Pi is not in scope for this procedure__.

Disclaimer
==========

This script-assisted process is provided as-is and its provider assumes no responsibility or liability for its use.

Included scripts
================

1. `setup.py` - Validates the checksums of the dependencies in the `depends/` subfolder and installs them on the Raspbian system.

2. `bip38-import.py` - Takes a BIP38 passphrase-encrypted private key and a passphrase and creates an Electrum wallet file in a RAM-held tmpfs location which can be given as a parameter to Electrum's CLI interface for subsequent operations.

3. `Electrum-3.0.4.tar.gz` - The full release of Electrum 3.0.4 will be unpacked and is subsequently usable on the image via the CLI and/or Python scripting interface. The GUI interface is not runnable due to the desktop environment not being included in the starting image.

4. `pybip38` - The entirety of this library is installed for the use of `bip38-import.py`. Its other API calls may also be useful.

Required Hardware
=================

For the airgapped system:
* Rasbperry Pi board
* Display
* USB Keyboard
* Power Suppy
* SD Card

For setting up the SD card:
* A reasonably secure system with access to this software. [TAILS](https://tails.boum.org/) is a good suggestion but please use your own judgement for for your security profile.
* A SD card reader

Software Dependencies
=====================

NOTE: this software has it's own terms and licences. The dependency packages are included here for convenience with checksums to help verify this is the exact known software intended under auditable revision control. The md5 and sha256 checksums are include the repository and are validated as part of `setup.py`. You are encouraged to validate the integrity of all these packages independently.

1. `2017-11-29-raspbian-stretch-lite.zip`
The official Raspbian lite OS image.
(not included in this repository, must be fetched from `http://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2017-12-01/2017-11-29-raspbian-stretch-lite.zip`)
sha256sum: `e942b70072f2e83c446b9de6f202eb8f9692c06e7d92c343361340cc016e0c9f`

2. `Electrum-3.0.4.tar.gz`
The official Electrum release.
Fetched from https://electrum.org/#download

3. `debs/*.deb`
27 Debian packages not included in the Raspbian lite image (`2017-11-29-raspbian-stretch-lite.zip`) which includes `python3-pip`, `libssl-dev` and all underlying dependencies. These are required for meeting the dependencies of `pybip38`. These were originally fetched via `aptitude` from an internet-connected Raspberry Pi.

4. `pips/*.whl`
5 pip3 packages which includes `pybip38`and underlying dependencies. These were originally fetched via `pip3` on an internet-connected Raspberry Pi.


OS Image Setup Instructions
===========================

1. Obtain and verify the Raspbian Lite OS image. This process is based off of `2017-11-29-raspbian-stretch-lite.zip`. Use `dd` to copy the image in `2017-11-29-raspbian-stretch-lite.zip` to the SD card. Example for the SD card appearing as `/dev/mmcblk0` on the host OS:

   ```
$ sha256sum 2017-11-29-raspbian-stretch-lite.zip
e942b70072f2e83c446b9de6f202eb8f9692c06e7d92c343361340cc016e0c9f  2017-11-29-raspbian-stretch-lite.zip
$ unzip 2017-11-29-raspbian-stretch-lite.zip
$ sudo dd if=2017-11-29-raspbian-stretch-lite.img of=/dev/mmcblk0 bs=1M status=progress
```

2. Eject the SD card:

   ```
$ sudo eject /dev/mmcblk0
```

3. Boot the Raspberry Pi with the SD card image to allow the filesystem to automatically resize and then log in when prompted (username: `pi`, password: `raspberry`).

4. While the Raspberry Pi is booted you may take the opportunity to set the keyboard map to `us` or whichever matches the keyboard you wish to use on this system:
   ```
$ sudo nano /etc/default/keyboard
```

and change the `gb` setting to `us`

5. Also, while the Raspberry Pi is booted take the opportunity to disable swap for additional security:

   ```
$ sudo apt-get remove dphys-swapfile
```

6. Also, while the Raspberry Pi is booted, take the opportunity to disable bash history for additional security:
   ```
$ history -c
$ sudo nano /etc/profile
```
and add `set +o history` to the bottom of the file

7. If you have a Raspberry Pi model with a wireless network interface, you might want to take the opportunity to hard disable it for additional security.

(instructions not included since it varies based on the Raspberry Pi model - if you have something reliable to say here, a pull request would be appreciated)

8. Safely shut down the Raspberry Pi and then move the SD card back to the host OS:

   ```
$ sudo poweroff
```

9. Mount the SD card's filesystem on the host and copy the `bip38-pi-airgap/` subdirectory to the `/home/pi/` on the card's filesystem:

   ```
$ cp -r /path/to/this/repo/bip38-pi-airgap /path/to/sdcard/mount/home/pi/
```

10. Unmount and eject the SD card after the copy has fully finished:

   ```
$ sudo sync
$ sudo umount /path/to/sdcard/mount/
$ sudo eject /dev/mmcblk0
```

11. Boot the Raspberry Pi and ensure that the copied directory has the correct user permissions for the `pi` user:

   ```
$ sudo chown -R pi /home/pi/bip38-pi-airgap
```

12. Run `setup.py` to validate the integrity of the copied files and perform the installation of the dependencies:

   ```
$ cd bip38-pi-airgap
$ ./setup.py
```

Wallet Setup Instructions
=========================

Running:

   ```
$ ./bip38-import.py <bip38-encrypted-key> <passphrase>
```

will decrypt the key with the passphrase and write a wallet file to `/run/user/1000/wallet`. This wallet file can be used as a parameter for the `electrum` cli utility unpacked to `/home/pi/bip38-pi-airgap/Electrum-3.0.4/`. Giving commands the parameter `-w /run/user/1000/wallet` will point Electrum at this wallet to use as the source of private keys.

Since this wallet file is held in tmpfs, it is not written to the SD card and will be lost if and when the Raspberry Pi is powered off.

Example Use
===========

Decrypt the key:
   ```
$ ./bip38-import.py 6PnPsnoRPCgbihtCbtGZGn2X2Xy1sKSp5CMCxWU4wridU1x331yeafep6n "This is an inadvisable passphrase."
[WalletStorage] wallet path /run/user/1000/wallet
[profiler] load_transactions 0.0000
[profiler] build_reverse_history 0.0000
[profiler] check_history 0.0000
decrypting...
decrypted key in 9.98634834 seconds
[WalletStorage] saved /run/user/1000/wallet
[profiler] write 0.0004
Finished creating wallet at /run/user/1000/wallet

Addresses in wallet:
        1P97WpopdbbpNiEfEqfGF8oQX8KTfQVJc1

This wallet can be used with the Electrum cli's '-w' parameter:

        $ ./electrum -w /run/user/1000/wallet

```
Sign a message with Electrum:
   ```
$ Electrum-3.0.4/electrum -w /run/user/1000/wallet signmessage 1P97WpopdbbpNiEfEqfGF8oQX8KTfQVJc1 "This is the message for testing purposes."
IJSbiLQNWjWZS6f8WIjY+8YfkaeEspwg/bWdzcIBMVCYBMqK+plw5B8pik6RFMVggp5O1yAm9lZrkPzic+EDp2U=
```

Verify the message signature with Electrum:
   ```
$ Electrum-3.0.4/electrum verifymessage 1P97WpopdbbpNiEfEqfGF8oQX8KTfQVJc1 IJSbiLQNWjWZS6f8WIjY+8YfkaeEspwg/bWdzcIBMVCYBMqK+plw5B8pik6RFMVggp5O1yAm9lZrkPzic+EDp2U= "This is the message for testing purposes."
true
```

Additional Airgapped Pi Tips
============================

1. [HDMI](https://en.wikipedia.org/wiki/HDMI) is a complex protocol and represents an attack surface. Using the Raspberry Pi's RCA analog video out is considered more secure. Transcribing encoded data may be difficult with the default font on an analog display. A different font from `/usr/shar/consolefonts/` can be set with the `setfont` command e.g.:
   ```
$ setfont /usr/share/consolefonts/Lat15-Terminus20x10.psf.gz
```

2. Avoid USB hubs and direct-connect your USB keyboard to the Pi. A hub could potentially hide keyloggers or other malicious devices.

3. Obtain an inexpensive USB keyboard that can be taken apart and inspected to help ensure there is no malicious tampering. Depending on your security profile, there are available designs for USB keyboards build out of simple parts.

4. There are known attacks for logging hidden data on SD cards. Depending on your security profile, consider destroying the SD card after the system has been in contact with private keys.

5. There is a significant amount of closed-source hardware design in the Raspberry Pi. Depending on your security profile, consider destroying the board after it has been in contact with private keys.

6. The Raspberry Pi's current draw from the power supply could theoretically leak partial information about a BIP38 passphrase or private key if monitored during the decryption process. A basic countermeasure is to use a simple 5 volt supply that can be inspected for malicious tampering. An advanced countermeasure is to add an additional quantity of electrical capacitance across the 5 volt input to help mask variations in current draw.


Note On Collecting/Validating the Software Dependencies
=======================================================
For use in repeating this process in the future to validate the software dependencies yourself:

To fetch the Debian package dependencies for `libssl-dev` and `python-pip`, on an internet-connected Raspberry Pi:
   ```
$ mkdir debs
$ sudo aptitude clean
$ sudo aptitude install --download-only libssl-dev python3-pip
$ cp /var/cache/apt/archives/*.deb debs
```

To fetch the pip dependencies for `pybip38`, on a internet-connected Raspberry Pi:
   ```
$ mkdir pips
$ pip3 download -d pips pybip38
```

You may then compare the downloaded files against the checksums with those in this repository.

   ```
$ sha256sum debs/*.deb pips/*.whl
$ md5sum debs/*.deb pips/*.whl
```
