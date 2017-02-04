#SignTransaction.py
# sign a transaction with multiple inputs and outputs
import struct
import base58
import hashlib
import ecdsa

# doing this for multiple inputs was harder than i thought it would be
# you need a different unsigend transaction hash for each input you sign
# with the scripts removed from the other inputs.
# since there are many libraries that do the job, decided to not spend any more time on this

fee = 4000
spend = [
    #{"address": "", "priv_key": "", "previous_txid": "", "value": "", index: "", compressed: True/False},
    {   "address": "n2JaMK3KvF1FY6x5L33CtmzSx2NaJDpjRL", 
        "priv_key": "14a8f3cc9b118c10fbb2ccf3a4dc892b03e0437d5ff42d3e13b142c7489328ee",
        "previous_txid": "2853b865985e2dccc6495c0a125c7185672f15acfe264b810870fa5ee7022c72",
        "value": "10000000",
        "index": 0,
        "compressed": False
    },
    {   "address": "mwU5JbdWBhzmNH7n78f66XNvgvPFwaHeUA", 
        "priv_key": "c90b144435e4b64fede67f1edfd6e1cdaeca7bf77704afda0b88931e7761a3db",
        "previous_txid": "a93f91523eee606c7b0bdd06f5d2ae5a7dd1293c4769c740ec0dce1280b6415e",
        "value": "10000000",
        "index": 1,
        "compressed": True
    },  
]
receive = [
    #{"address": "", "amount": 10000},
    {"address": "mjSdarBSEBCN3bKGpN4w6F7441ttN9eyZ9", "value": 10000000 - fee},
    #{"address": "mziXvDdvrG3ZoX9AVzwsRxC3x5RH9h2RtV", "value": 7000000 },
    #{"address": "msumJZWwZP9Q636qe5YShqY7JqkhaJFWhE", "value": 3000000 },
    #{"address": "mv7Yen4XCJ59dAZsnUnVQkr6YDpdx1oqFz", "value": 10000000 },
]

class raw_tx:
    def __init__(self, in_count, out_count, lock_time=0, version=1):
        self.version      = struct.pack("<L", version)
        self.input       = []
        self.tx_in_count  = struct.pack("<B", in_count)
        for i in range(0, in_count):
            self.input.append({})
        self.output      = []
        self.tx_out_count = struct.pack("<B", out_count)
        for i in range(0, out_count):
            self.output.append({})
        self.lock_time    = struct.pack("<L", lock_time)

def flip_bytes(string):
    flipped = "".join(reversed([string[i:i+2] for i in range(0, len(string), 2)]))
    return flipped

def build_tx(tx, signed=0):
    t = tx.version
    # inputs
    t += tx.tx_in_count
    for i in range (0, len(tx.input)):
        t += tx.input[i]["txouthash"]
        t += tx.input[i]["tx_out_index"]
        if signed < 1:
            t += tx.input[i]["script_bytes"]
            t += tx.input[i]["script"]
        else:
            t += tx.input[i]["sigscript_length"]
            t += tx.input[i]["signature_length"]
            t +=  tx.input[i]["sigscript"]
        t += tx.input[i]["sequence"]

    # outputs
    t += rtx.tx_out_count
    for i in range (0, len(tx.output)):
        t += tx.output[i]["value"]
        t += tx.output[i]["pk_script_bytes"]
        t += tx.output[i]["pk_script"]
    t += tx.lock_time
    if signed < 1: t += struct.pack("<L", 1)
    return t

# new raw transaction
rtx = raw_tx(len(spend),len(receive))
# inputs
for i in range(0, len(spend)):
    # hash the pub key
    spend[i]["pub_key_hash"] = base58.b58decode_check(spend[i]["address"])[1:].encode("hex")
    # add this input
    rtx.input[i]["txouthash"]    = flip_bytes(spend[i]["previous_txid"]).decode("hex")
    rtx.input[i]["tx_out_index"] = struct.pack("<L", spend[i]["index"])
    rtx.input[i]["script"]       = ("76a914%s88ac" % spend[i]["pub_key_hash"]).decode("hex")
    rtx.input[i]["script_bytes"] = struct.pack("<B", (len(rtx.input[i]["script"])))
    rtx.input[i]["sequence"]     = "ffffffff".decode("hex")
# outputs
for i in range(0, len(receive)):
    # hash of the pub key
    receive[i]["pub_key_hash"]   = base58.b58decode_check(receive[i]["address"])[1:].encode("hex")
    # add this output
    rtx.output[i]["value"]       = struct.pack("<Q", receive[i]["value"])
    rtx.output[i]["pk_script"]   = ("76a914%s88ac" % receive[i]["pub_key_hash"]).decode("hex")
    rtx.output[i]["pk_script_bytes"] = struct.pack("<B", (len(rtx.output[i]["pk_script"])))

# buld the transaction
unsigned_transaction = build_tx(rtx)
# make a hash of the transaction to sign
unsigned_transaction_hash = hashlib.sha256(hashlib.sha256(unsigned_transaction).digest()).digest()

# sign each of the inputs
for i in range(0, len(spend)):
    sk = ecdsa.SigningKey.from_string(spend[i]["priv_key"].decode("hex"), curve = ecdsa.SECP256k1)
    vk = sk.verifying_key
    verify = vk.to_string().encode("hex")
    #print verify
    if spend[i]["compressed"]:
        # we only need to know if Y is even or odd
        if int(verify[-1],16) % 2:
            public_key = '03' + verify[:len(verify)//2]
        else:
            public_key = '02' + verify[:len(verify)//2]
    else:
        public_key = '04' + verify
    #print public_key;print
    signature = sk.sign_digest(unsigned_transaction_hash, sigencode = ecdsa.util.sigencode_der)
    sigscript = (
        signature + "\01"
        + struct.pack("<B", len(public_key.decode("hex")))
        + public_key.decode("hex")
    )
    rtx.input[i]["sigscript"]        =  sigscript
    rtx.input[i]["sigscript_length"] =  struct.pack("B", len(sigscript) +1)
    rtx.input[i]["signature_length"] =  struct.pack("B", len(signature) +1)

# build the signed transaction
signed_transaction = build_tx(rtx, 1)
#print unsigned_transaction.encode("hex") + "\n"
print signed_transaction.encode("hex")
