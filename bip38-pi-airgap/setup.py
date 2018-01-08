#!/usr/bin/env python3
import os
import sys
import subprocess

def run_cmd(cmd):
    rc = subprocess.call(cmd)
    return rc == 0

def dir_files(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.join(dirpath, f)

print("validate the integrity of the files:\n")
cmd = ['md5sum', '-c', 'md5sums.txt']
if not run_cmd(cmd):
    sys.exit("md5 sums don't match!")
cmd = ['sha256sum', '-c', 'sha256sums.txt']
if not run_cmd(cmd):
    sys.exit("sha256 sums don't match!")
print("OK\n")

print("install Raspbian .deb pagkages:\n")
cmd = ['sudo', 'dpkg', '-i'] + list(dir_files('depends/debs/'))
if not run_cmd(cmd):
    sys.exit("debian packages not installed")
print("OK\n")

print("install pip3 .whl pagkages:\n")
cmd = (['sudo', 'pip3', 'install'] +
       list(dir_files('depends/pips')))
if not run_cmd(cmd):
    sys.exit("pip .whl packages not installed")
print("OK\n")

print("Extract electrum:\n")
cmd = ['tar', '-zxpvf', 'depends/Electrum-3.0.5.tar.gz']
if not run_cmd(cmd):
    sys.exit("Electrum not extracted")
print("OK\n")

print("System successfully set up!\n")
