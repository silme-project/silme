#!/usr/bin/python
# Copyright (c) 2018 CVSC
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.



import struct 
import hashlib
from construct import *
from pybitcointools import *
from binascii import hexlify, unhexlify, b2a_hex, a2b_hex
import sys
from os.path import expanduser
from sys import platform
import os 
import string 
import random 
import logging
import time
import socket


nMaxSize = 1000000 # 1MB
# One silme can be split into 100000000 satoshi
COIN = 100000000


def generate_nodeid():
    return hashlib.sha256(os.urandom(256/8)).hexdigest()


def GetAppDir():
    # currently suppports linux 
    if not platform == "linux":
        if not platform == "linux2":
            sys.exit(logg("Error: Unsupported platform"))
    return expanduser("~") + "/" + ".silme"


def internetConnection(host="8.8.8.8", port=53, timeout=3):
    
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        return False




def logg(msg):
	logging.basicConfig(level=logging.INFO, filename=GetAppDir() + "/debug.log", format='%(asctime)s %(message)s') # include timestamp

	logging.info(msg)



def decode_uint32(self): return struct.unpack("<I", self)[0]
def format_hash(hash_): return str(hexlify(hash_[::-1]).decode("utf-8"))


class CTransaction(dict):

    def __init__(self):
        self = dict()
        self.clear()

    def input_script(self, message):
        psz_prefix = ""
        #use OP_PUSHDATA1 if required
        if len(message) > 76: psz_prefix = '4c'
        script_prefix = '04ffff001d0104' + psz_prefix + chr(len(message)).encode('hex')
        input_script_f  = (script_prefix + message.encode('hex')).decode('hex')
        self.add("input_script", input_script_f)

    def output_script(self, pubkey):
        script_len = '41'
        OP_CHECKSIG = 'ac'
        output_script_f = (script_len + pubkey + OP_CHECKSIG).decode('hex')
        self.add("output_script", output_script_f)


    def add(self, key, value):
        self[key] = value




    def clear(self):
        # clear the dict 
        self.clear()



    def getHash(self):
        # transaction hash 
        return hashlib.sha256(hashlib.sha256(str(self)).digest()).digest()



def target2bits(target):
        MM = 256*256*256
        c = ("%064X"%int(target))[2:]
        i = 31
        while c[0:2]=="00":
            c = c[2:]
            i -= 1
        c = int('0x'+c[0:6],16)
        if c >= 0x800000:
            c //= 256
            i += 1
        new_bits = c + MM * i
        return new_bits


def num2mpi(n):
        """convert number to MPI string"""
        if n == 0:
                return struct.pack(">I", 0)
        r = ""
        neg_flag = bool(n < 0)
        n = abs(n)
        while n:
                r = chr(n & 0xFF) + r
                n >>= 8
        if ord(r[0]) & 0x80:
                r = chr(0) + r
        if neg_flag:
                r = chr(ord(r[0]) | 0x80) + r[1:]
        datasize = len(r)
        return struct.pack(">I", datasize) + r



def GetCompact(n):
    """convert number to bc compact uint"""
    mpi = num2mpi(n)
    nSize = len(mpi) - 4
    nCompact = (nSize & 0xFF) << 24
    if nSize >= 1:
        nCompact |= (ord(mpi[4]) << 16)
    if nSize >= 2:
        nCompact |= (ord(mpi[5]) << 8)
    if nSize >= 3:
        nCompact |= (ord(mpi[6]) << 0)
    return nCompact


def bits2target(bits):
    """ Convert bits to target """
    exponent = ((bits >> 24) & 0xff)
    mantissa = bits & 0x7fffff
    if (bits & 0x800000) > 0:
        mantissa *= -1 
    return (mantissa * (256**(exponent-3)))