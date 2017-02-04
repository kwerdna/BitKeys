# many addresses from one pub key
import sys
from bitcoin import *
import base58
from fastecdsa import keys, curve

minsigs = 2
maxsigs = 3
if len(sys.argv) == 3:
	minsigs = int(sys.argv[1])
	maxsigs = int(sys.argv[2])
	if maxsigs > 16: maxsigs = 16;
	if minsigs > maxsigs: minsigs = maxsigs -1;
 
def returnkeys(n):
	myarray = []
	for i in range(n):
		data = {'priv': keys.gen_private_key(curve.P256) } 
		# there are 2 possible addresses for each private key
		# we encode the private key to indicate the desired public key format
		data['uncompressed'] = {'wif': encode_privkey(data['priv'], 'wif')}
		data['compressed'] = {'wif': encode_privkey(data['priv'], 'wif_compressed')}
		for c in ('compressed', 'uncompressed'):
			# pub will be compressed or not based on the wif format 
			data[c]['pub'] =  privtopub(data[c]['wif'])
			# btc address
			data[c]['btc'] =  pubtoaddr(data[c]['pub'])
			# testnet (same address for litecoin testnet)
			data[c]['tbtc'] =  pubtoaddr(data[c]['pub'], 111)
			# some alt coins
			data[c]['ltc'] =  pubtoaddr(data[c]['pub'], 48)
			data[c]['tltc'] =  pubtoaddr(data[c]['pub'], 111)
			data[c]['doge'] =  pubtoaddr(data[c]['pub'], 30)
			data[c]['tdoge'] =  pubtoaddr(data[c]['pub'], 113)
			data[c]['dash'] =  pubtoaddr(data[c]['pub'], 76)
			data[c]['tdash'] =  pubtoaddr(data[c]['pub'], 5) # need to verify this is the right base58 prefix
			data[c]['hashed'] =  base58.b58decode_check(data[c]['btc'])[1:].encode("hex")
			data[c]['hashedl'] =  base58.b58decode_check(data[c]['ltc'])[1:].encode("hex")
			data[c]['hashedd'] =  base58.b58decode_check(data[c]['doge'])[1:].encode("hex")
		myarray.append(data)
	return (myarray)

# make key pairs
print 'Making {} key pairs'.format(maxsigs)
keypairs = returnkeys(maxsigs)

# print from data structure
for key in keypairs:
	print("priv key : {}".format(key['priv']))
	for c in ('compressed', 'uncompressed'):
		print("{}".format(c))
		print("   priv wif: {}".format(key[c]['wif']))
		print("   pub     : {}".format(key[c]['pub']))
		print("   btc     : {}".format(key[c]['btc']))
		print("   tbtc    : {}".format(key[c]['tbtc']))
		print("   ltc     : {}".format(key[c]['ltc']))
		print("   doge    : {}".format(key[c]['doge']))
		print("   tdoge   : {}".format(key[c]['tdoge']))
		print("   dash    : {}".format(key[c]['dash']))
		print("   tdash   : {}".format(key[c]['tdash']))
		print("   hashed   : {}".format(key[c]['hashed']))
		print("   hashedl   : {}".format(key[c]['hashedl']))
		print("   hashedd   : {}".format(key[c]['hashedd']))
	print "=*=" * 10 

# make the multi sig script and address
print("Making {} of {} multisig address with compressed pub keys".format(minsigs, maxsigs))
multisig_redeem_script = mk_multisig_script([p['compressed']['pub'] for p in keypairs], minsigs, maxsigs)
multisig_address = scriptaddr(multisig_redeem_script) # main net (also litecoin multisig address)
testnet_multisig_address = scriptaddr(multisig_redeem_script, 196) # testnet (also litecoin testnet)
doge_multisig_address = scriptaddr(multisig_redeem_script, 22) # doge
dash_multisig_address = scriptaddr(multisig_redeem_script, 16) # dash

print("btc    : {}".format(multisig_address))
print("tbtc   : {}".format(testnet_multisig_address))
print("doge   : {}".format(doge_multisig_address))
print("dash   : {}".format(dash_multisig_address))
print("redeem :({}bytes) {}".format(len(multisig_redeem_script)/2, multisig_redeem_script))

for i in range(len(keypairs)):
	print "pk{}: {}".format(i+1, keypairs[i]['compressed']['wif'])
