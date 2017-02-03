#SignTransaction.py
# sign a transaction
import struct
import base58
import hashlib
import ecdsa

inputs = [
	{}
]
outputs = [
	{}
]

# the spending address(es)
spending_addr = 'mmNDXPmpU1rpaP5uk7hri6wS865kvdAMQK'
priv_key = '0f7ae94fc1fb5a42ad943cb1cbc0fea2c220050c087fff3cfc733885a17a0d46' # hash of jpg file
spending_pub_key_hash = base58.b58decode_check(spending_addr)[1:].encode("hex")
previous_txid = 'f362e63bbfba199e177730d99196662fd693520dc1a2f7b0ac773b3e089d0aa4'
satoshis = 10000

return_address = 'mxpES43L2m8S9stHt7uy24EKQcj3XAzkMz'
return_pub_key_hash = base58.b58decode_check(return_address)[1:].encode("hex")

explore_url = 'https://chain.so/tx/BTCTEST/f362e63bbfba199e177730d99196662fd693520dc1a2f7b0ac773b3e089d0aa4'

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
	t = tx.version + tx.tx_in_count
	for i in range (0, len(tx.input)):
		t += (
			tx.input[i]["txouthash"]
			+ tx.input[i]["tx_out_index"]
		)
		if signed <1:
			t += tx.input[i]["script_bytes"]
			t +=	tx.input[i]["script"]
		else:
			t += tx.input[i]["sigscript_length"]
			t += tx.input[i]["signature_length"]
			t += tx.input[i]["sigscript"]

		t += tx.input[i]["sequence"]
	t += rtx.tx_out_count
	for i in range (0, len(tx.output)):
		t += (
		tx.output[i]["value"]
		+ tx.output[i]["pk_script_bytes"]
		+ tx.output[i]["pk_script"]
		)
	t += tx.lock_time
	if signed < 1: t += struct.pack("<L", 1)
	return t

# new raw transaction
rtx = raw_tx(1,1)
# inputs
rtx.input[0]["txouthash"]    = flip_bytes(previous_txid).decode("hex")
rtx.input[0]["tx_out_index"] = struct.pack("<L", 1)
rtx.input[0]["script"]       = ("76a914%s88ac" % spending_pub_key_hash).decode("hex")
rtx.input[0]["script_bytes"] = struct.pack("<B", (len(rtx.input[0]["script"])))
rtx.input[0]["sequence"]     = "ffffffff".decode("hex")


# outputs
rtx.output[0]["value"]           = struct.pack("<Q", satoshis)
rtx.output[0]["pk_script"]       = ("76a914%s88ac" % return_pub_key_hash).decode("hex")
rtx.output[0]["pk_script_bytes"] = struct.pack("<B", (len(rtx.output[0]["pk_script"])))

unsigned_tx_string = build_tx(rtx)
# we sign a hash of the transaction
unsigned_tx_hash = hashlib.sha256(hashlib.sha256(unsigned_tx_string).digest()).digest()
#print unsigned_tx_hash.encode("hex")

print unsigned_tx_string.encode("hex");print
# sign each input with corresponding private key
sk = ecdsa.SigningKey.from_string(priv_key.decode("hex"), curve = ecdsa.SECP256k1)
vk = sk.verifying_key
public_key = ('\04' + vk.to_string()).encode("hex")
signature = sk.sign_digest(unsigned_tx_hash, sigencode = ecdsa.util.sigencode_der)
sigscript = (
	signature
	+ "\01"
	+ struct.pack("<B", len(public_key.decode("hex")))
	+ public_key.decode("hex")

)
# add the signatures for thsi input to the tx
rtx.input[0]["sigscript"]       =  sigscript
rtx.input[0]["sigscript_length"] =  struct.pack("B", len(sigscript) +1)
rtx.input[0]["signature_length"] =  struct.pack("B", len(signature) +1)

# build thge signed transaction
signed_transaction = build_tx(rtx, 1)
print signed_transaction.encode("hex")

