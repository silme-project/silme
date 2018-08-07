#!/usr/bin/python
# Copyright (c) 2018 CVSC
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from bitcoin import *
from dboperations import * 
from consensus import *




if not os.path.exists(GetAppDir()):
    # db isn't initalized, initialize it
    try:
        os.mkdir(GetAppDir())
        logg("First run detected")
    except Exception, e:
        raise
    else:
        logg("Initializing Blockchain / Wallet database")
        CBlockchain(Genesis=True)
        CWalletDB()

if not os.path.exists(GetAppDir() + "/silme.conf"):
    sys.exit("Please run ./configure first")


class CKey(object):

    # CKey class use https://github.com/vbuterin/pybitcointools

    def MakeNewKey(self):
        rand_str = lambda n: ''.join([random.choice(string.lowercase) for i in xrange(n)])
        return sha256(rand_str(10))


    def GetPubKey(self, priv):
        return privtopub(priv)



    def GetAddress(self, pub):
        return pubtoaddr(pub)







class CBlock(object):
    
    def __init__(self):
        # block header
        self.nVersion = None       # version 
        self.hashPrevBlock = None  # previous block hash 
        self.hashMerkleRoot = None # merkle 
        self.nTime = None          # time 
        self.nBits = None          # bits 
        self.nNonce = None         # nonce

        self.vtx = []
        self.vMerkleTree = []


    def CBlock(self):
        SetNull()



    def SetNull(self):
        self.nVersion = 1
        self.hashPrevBlock = 0
        self.hashMerkleRoot = 0
        self.nTime = 0
        self.nBits = 0
        self.nNonce = 0
        del self.vtx[:]
        del self.vMerkleTree[:]


    def IsNull(self):
        return self.nBits == 0




    def Nullvtx(self):
        del self.vtx[:]




    def BuildMerkleTree(self):
        del self.vMerkleTree[:]


        if len(self.vtx) == 1:
            return hashlib.sha256(hashlib.sha256(str(self.vtx[0])).hexdigest()).hexdigest()

        for tx in self.vtx:
            self.vMerkleTree.append(hashlib.sha256(hashlib.sha256(str(tx)).hexdigest()).hexdigest())


        return hashlib.sha256(hashlib.sha256(str(self.vMerkleTree)).hexdigest()).hexdigest()



class tmp():
    
    nVersion = None 
    hashPrevBlock = None
    hashMerkleRoot = None 
    nTime = None 
    nBits = None 
    nNonce = None 

    def hex_to_hash(self, h):
        return b''.join((unhexlify(h)))

    def build(self):
        block_header = Struct("block_header",
          Bytes("version",4),
          Bytes("hash_prev_block", 32),
          Bytes("hash_merkle_root", 32),
          Bytes("time", 4),
          Bytes("bits", 4),
          Bytes("nonce", 4))

        Cblock = block_header.parse('\x00'*80)
        Cblock.version          = struct.pack('<I', 1)
        Cblock.hash_prev_block  = struct.pack('>32s', self.hex_to_hash(self.hashPrevBlock))
        Cblock.hash_merkle_root = struct.pack('>32s', str(self.hashMerkleRoot))
        Cblock.time             = struct.pack('<I', self.nTime)
        Cblock.bits             = struct.pack('<I', self.nBits)
        Cblock.nonce            = struct.pack('<I', self.nNonce)
        return block_header.build(Cblock)


class Proccess(object):


    def thisBlock(self, block, pblock, nonce):
        logg("Proccessing new block\n")
        # calculate hash 
        block_hash = hashlib.sha256(hashlib.sha256(block).digest()).digest()[::-1].encode('hex_codec')

        
        # Check for duplicate
        if CBlockchain().haveHash(block_hash):
            logg("Proccess().thisBlock : already have block %s %s" %(CBlockIndex(block_hash).Height(), block_hash,))
            return False 
        
        # Check prev block
        if CBlockchain().GetBestHash() != block[8:72]:
            logg("Proccess().thisBlock : prev block not found")
            return False

        # Check timestamp against prev
        if CBlockIndex(CBlockchain().GetBestHash()).Time() >= decode_uint32(a2b_hex(block[136:144])):
            logg("Proccess().thisBlock : block's timestamp is too early")
            return False


        # Check Proof Of Work
        if decode_uint32(a2b_hex(block[144:152])) != GetNextWorkRequired():
            logg("Proccess().thisBlock : incorrect proof of work")
            return False



        # check merkle root 
        if pblock.hashMerkleRoot != pblock.BuildMerkleTree():
            logg("Proccess().thisBlock : Merkle root mismatch")
            return False 

        # Check size 
        if sys.getsizeof(pblock.vtx) > nMaxSize:
            logg("Proccess().thisBlock : Block size failed")
            return False


        # Preliminary checks
        if self.CheckBlock(block, pblock, nonce):
            return True 


    def CheckBlock(self, block, pblock, nonce):

       
        # be sure that first tx is coinbase
        if not pblock.vtx[0]["prev_out"] == 0:
            logg("Proccess().CheckBlock : first tx is not coinbase")
            return False

        # be sure that only 1 coinbase tx included 
        for x in xrange(1,len(pblock.vtx)):
            if pblock.vtx[x]["prev_out"] == 0:
                logg("Proccess().CheckBlock : more than one coinbase")
                return False
        
        # check transactions, not include coinbase tx 
        for x in xrange(1,len(pblock.vtx)):
            if not self.thisTxIsVaild(pblock.vtx[x]):
                logg("Proccess().CheckBlock : Invaild tx found")
                return False
        

        # verify input sig
        for x in xrange(1,len(pblock.vtx)):
            if not CBlockchain().isVaildTx(pblock.vtx[x]):
                logg("Proccess().CheckBlock : Failed to verify input sig")
                return False
   
        return True



    def thisTxIsVaild(self, tx):
        # check transaction verification
        
        # store signature in memory
        signature = tx["signature"]
        # remove signature from tx
        del tx["signature"]

        pub = CTx(tx["prev_out"]).GetRecipten()

        try:
            ecdsa_verify(str(tx),signature,pub)
            tx['signature'] = signature
        except Exception, e:
            tx['signature'] = signature
            logg("Transaction %s verification error" %hashlib.sha256(hashlib.sha256(str(tx)).digest()).digest().encode("hex_codec"))
            logg(e)
            return False


        
        # check for empty scripts 
        if len(tx["input_script"]) < 10 or len(tx["output_script"]) < 10:
            logg("Proccess::thisTxIsVaild() : vin or vout empty")
            return False
        
        # check for negative tx value
        if tx["value"] == 0:
            logg("Proccess::thisTxIsVaild() : txout.nValue negative")
            return False
        
        # check for missing prevout 
        if tx["prev_out"] == 0:
            logg("Proccess::thisTxIsVaild() : prevout is null")
            return False

        # check if have coins to spend

        # get the sender pubkey of the input hash 
        thisPrev = CTx(tx["prev_out"]).GetRecipten()

        if CBlockchain().GetBalance(thisPrev) < tx["value"]:
            logg("Proccess::thisTxIsVaild() : %s not enough coins to spend" %hashlib.sha256(hashlib.sha256(str(tx)).digest()).digest().encode("hex_codec"))
            return False  


        return True




def AddKey(pkey):
    key = CKey()
    pubkey = key.GetPubKey(pkey)
    return CWalletDB().WriteKey(pkey, pubkey)





def GenerateNewKey():
    key = CKey()
    pkey = key.MakeNewKey()

    if not AddKey(pkey):
        sys.exit(logg("GenerateNewKey() : AddKey failed\n"))
    return key.GetPubKey(pkey)



def GetBlockValue(height, fees):
    subsidy = nCoin * COIN
    subsidy >>= (height / nSubsibyHalvingInterval)
    return subsidy + fees





def GetNextWorkRequired():

    # latest block hash 
    pindexLast = CBlockchain().GetBestHash()
    
    # Difficulty will change every 600 seconds or 10 minuntes
    nTargetTimespan = 600 
    # We need a new block every 100 seconds
    nTargetSpacing = 100
    # That give us a interval 4 blocks
    nInterval = nTargetTimespan / nTargetSpacing / 2
    
    
    # if the last block height == 1 return the minimun diif
    if CBlockIndex(pindexLast).Height() == 1:
        return 0x1e0fffff


    # Only change once per interval
    if ((CBlockIndex(pindexLast).Height()+1) % nInterval != 0):
        # Return the last block bits (difficulty)
        return CBlockIndex(pindexLast).Bits()


    # Go back by what we want to be 10 minuntes worth of blocks
    # nActualTimespan is the avg time of the last 6 blocks, example if each of the last 6 blocks took 30 seconds nActualTimespan will be 180
    nActualTimespan = CBlockIndex(pindexLast).Time() - CBlockIndex(CBlockIndex(pindexLast).Height() - nInterval + 2).Time()
    # so if the nActualTimespan is bigger the nTargetTimespan means that blocks are mined slowly, difficulty will be reduced,
    # if the nActualTimespan is lower than nTargetTimespan means that blocks are mined quick, difficulty will be increased

    logg("nActualTimespan = %d  before bounds\n" %nActualTimespan)

    if nActualTimespan < nTargetTimespan/4:
        nActualTimespan = nTargetTimespan/4
    if nActualTimespan > nTargetTimespan*4:
        nActualTimespan = nTargetTimespan*4

    bnNew = bits2target(CBlockIndex(pindexLast).Bits())
    bnNew *= nActualTimespan
    bnNew /= nTargetTimespan

    if bnNew > bnProofOfWorkLimit:
        bnNew = bnProofOfWorkLimit

    

    logg("\n\n\nGetNextWorkRequired RETARGET *****\n")
    logg("nTargetTimespan = %d    nActualTimespan = %d\n" %(nTargetTimespan, nActualTimespan,))
    logg("Last %d blocks time average was %d\n" %(nInterval, nActualTimespan,))
    logg("Before: %08x  %s\n" %(CBlockIndex(pindexLast).Bits(), nActualTimespan,))
    logg("After:  %08x  %s\n" %(GetCompact(int(bnNew)), nActualTimespan,))

    return target2bits(bnNew)


def CalculateDiff(bits=None):
    """ Calculate current difficulty """
    # diff is minimun difficulty target / current_target 
    if bits:
        p = bits2target(bits)
    else:
        p = bits2target(0x1d00ffff)
    y = bits2target(GetNextWorkRequired())
    return float(p) / float(y)


def NetworkHashrate():
    # network hashrate in ghs
    difficulty = CalculateDiff()
    return difficulty * 2**32 / 100 / 1000000000

   

def HashesTowin():
    """ Calculate required hashes to find a block """
    return CalculateDiff() * 2**256 / (0xffff * 2**208)



def generate_hashes_from_block(data_block):
    sha256_hash = hashlib.sha256(hashlib.sha256(data_block).digest()).digest()[::-1]
    return sha256_hash, sha256_hash




def generate_hash(data_block, targetx):
    nonce           = 0
    target = targetx
    last_updated = time.time()

    while True:
        sha256_hash, header_hash = generate_hashes_from_block(data_block)
        if int(header_hash.encode('hex_codec'), 16) < target:
            return (sha256_hash, nonce, data_block)
        else:
            nonce      +=1
            data_block = data_block[0:len(data_block) - 4] + struct.pack('<I', nonce)  
  


class CaBlock(object):
    def __init__(self, thisHeight):
        self.raw_block = CBlockIndex(thisHeight).Raw()
        self.nonce = CBlockIndex(thisHeight).Nonce()
        self.txs = CBlockIndex(thisHeight).Txs()
        self.readytxs = []
        self.pblock_ = None 
        self.cltxs()



    def pblock(self):
        pblock = CBlock()
        pblock.Nullvtx()
        for tx in self.readytxs:
            pblock.vtx.append(tx)
        pblock.hashMerkleRoot = pblock.BuildMerkleTree()
        self.pblock_ = pblock
        
    

    def cltxs(self):
        for tx in self.txs:
            txhash = tx[5]
            if tx[2] == 0:
                # coinbase transaction
                CCoinbase = CTransaction()
                CCoinbase.add("version", CTx(txhash).Version())
                CCoinbase.add("prev_out", CTx(txhash).Prev())
                CCoinbase.add("time", CTx(txhash).Time())
                CCoinbase.input_script("")
                CCoinbase.output_script(CTx(txhash).GetRecipten())
                CCoinbase.add("value", CTx(txhash).Value())
                CCoinbase.add("signature", CTx(txhash).GetSignature())
                self.readytxs.append(CCoinbase)
            else:

                txNew = CTransaction()
                txNew.add("version", CTx(txhash).Version())
                txNew.add("prev_out", CTx(txhash).Prev())
                txNew.add("time", CTx(txhash).Time())
                txNew.add("input_script", CTx(txhash).InsScript())
                txNew.add("output_script", CTx(txhash).OutScript())
                txNew.add("value", CTx(txhash).Value())
                txNew.add("signature", CTx(txhash).GetSignature())
                self.readytxs.append(txNew)


        self.pblock()

    def dump(self):
        return self.raw_block, self.pblock_, self.nonce
