#!/usr/bin/python
# Copyright (c) 2018 CVSC
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from bitcoin import *
from dboperations import * 



# One silme can be split into 100000000 satoshi
COIN = 100000000
# Proof of Work limit 
bnProofOfWorkLimit = 0x00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
# Reward Per block
nCoin = 50
# Halving Every 210000 blocks
nSubsibyHalvingInterval = 210000
# MaxBlockSize
nMaxSize = 1000000 # 1MB

COINBASE_MATURITY = 4



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

    # block header
    nVersion = None       # version 
    hashPrevBlock = None  # previous block hash 
    hashMerkleRoot = None # merkle 
    nTime = None          # time 
    nBits = None          # bits 
    nNonce = None         # nonce

    vtx = []
    vMerkleTree = []


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
        conn = sqlite3.connect(GetAppDir() + "/blockchain.db")
        conn.text_factory = str
        cur = conn.cursor()

        
        # store signature in memory
        signature = tx["signature"]
        # remove signature from tx
        del tx["signature"]

        pub = cur.execute("SELECT output_script FROM transactions where hash = ?", (tx["prev_out"],)).fetchone()[0].encode("hex_codec")[2:132]

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



class CAserialize(object):
    def __init__(self, obj):
        self.block = obj
        self.blockheader = self.block[0:160]
        self.num_txs = self.numtxs()
        self.transactions = []
        self.gettxs()


    def build(self):
        pblock = CBlock()
        pblock.Nullvtx()
        

        for tx in self.transactions:
            pblock.vtx.append(tx)

        return self.blockheader, pblock


    def gettxs(self):
        for x in xrange(int(self.num_txs) -1):
            tx = self.block[160: len(raw)].split("#")
            txs = tx[x +1].split("@")
        for tx in txs:
            self.transactions.append(tx.decode("hex"))

    def numtxs(self):
        return self.block[160: len(raw)].split("#")[0]






class thisBlock(object):

    # Proccess new block received by peer, and add it to database if is vaild
    # Return True if vaild False if Not
    # Only proccess blocks with coinbase transaction, wil be fixed later
    


    def __init__(self, peer, raw, coinbase, transactions, nonce):
        self.ThisPeer = peer
        self.thisRaw = raw
        self.thisCoinbase = coinbase
        self.thisTransactions = transactions
        self.thisNonce = nonce



    def isVaild(self):
        blk, pblock, = self.Build()
        blk = blk[0:len(blk) - 4] + struct.pack('<I', self.thisNonce)  
        if Proccess().thisBlock(blk, pblock, self.thisNonce):
          logg("Block accepted\n")
          if CBlockchain().WriteBlock(pblock, blk, self.thisNonce):
            logg("Block successfull added to database") 
            return True
        return False 



    def Build(self):
        pblock = CBlock()
        pblock.Nullvtx()
        

        txNew = CTransaction()
        txNew.add("version", self.thisCoinbase[1])
        txNew.add("prev_out", self.thisCoinbase[2])
        txNew.add("time", self.thisCoinbase[3])
        txNew.add("value", self.thisCoinbase[4])
        txNew.add("input_script", self.thisCoinbase[6])
        txNew.add("output_script", self.thisCoinbase[7])
        txNew.add("signature", self.thisCoinbase[8])
        

        pblock.vtx.append(txNew)

        
        pblock.nTime = decode_uint32(a2b_hex(self.thisRaw[136:144]))
        pblock.nBits = decode_uint32(a2b_hex(self.thisRaw[144:152]))

        tmp_block = tmp()

        tmp_block.nVersion = 1 
        tmp_block.hashPrevBlock = self.thisRaw[8:72]
        tmp_block.hashMerkleRoot = a2b_hex(self.thisRaw[72:136])
        tmp_block.nTime = pblock.nTime
        tmp_block.nBits = pblock.nBits
        tmp_block.nNonce = 0  

        blk = tmp_block.build().encode("hex_codec")
        return blk, pblock




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


def CalculateDiff():
    """ Calculate current difficulty """
    # diff is minimun difficulty target / current_target 
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
        for tx in self.readytxs:
            pblock.vtx.append(tx)
        pblock.hashMerkleRoot = pblock.BuildMerkleTree()
        self.pblock_ = pblock
        
    

    def cltxs(self):
        for tx in self.txs:
            if tx[2] == 0:
                txhash = tx[5]
                # coinbase transaction
                txNew = CTransaction()
                txNew.add("version", CTx(txhash).Version())
                txNew.add("prev_out", CTx(txhash).Prev())
                txNew.add("time", CTx(txhash).Time())
                txNew.input_script("")
                txNew.output_script(CTx(txhash).GetRecipten())
                txNew.add("value", CTx(txhash).Value())
                txNew.add("signature", CTx(txhash).GetSignature())
                self.readytxs.append(txNew)
        self.pblock()

    def dump(self):
        return self.raw_block, self.pblock_, self.nonce
