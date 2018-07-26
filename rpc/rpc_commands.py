#!/usr/bin/python
# Copyright (c) 2018 CVSC
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from main import CKey, GenerateNewKey
from main import GetNextWorkRequired
from dboperations import *
from version import _version




def CalculateDiff():
    """ Calculate current difficulty """
    # diff is minimun difficulty target / current_target 
    p = bits2target(0x1d00ffff)
    y = bits2target(GetNextWorkRequired())
    return "{0:.6f}".format(float(p) / float(y))




def GetBestHeight():
    # return best heigh 
    return CBlockchain().getBestHeight()

def GetBestHash():
    # return the best hash in blockchain
    return CBlockchain().GetBestHash()


def GetDifficulty():
    # return the difficulty
    return CalculateDiff()


def GetMyAddresses():
    # return all addresses that we own
    return CWalletDB().GetMyAddresses()


def GetNewAddress():
    # return new address
    key = GenerateNewKey()
    return CKey().GetAddress(key)

def NetHashRate():
    # return network hashrate in ghs
    return NetworkHashrate()

def GetBalance():
    return CWalletDB().GetBalance()


def GetRaw(self, obj):
    pass


def MemCount():
    return MemPool().CountTxs()


def Version():
    return _version


def GetInfo():
    data = {"data": {"blocks": GetBestHeight(), 
                     "hash": GetBestHash(), 
                     "difficulty": GetDifficulty(),
                     "version": Version(),
                     "balance": GetBalance()}}
    return data


def GetTarget():
    return str(bits2target(GetNextWorkRequired()))
