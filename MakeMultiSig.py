# many addresses from one pub key
import sys
from bitcoin import *
import base58

# usage: python MakeMultiSig.py min max
# defaults to 2 of 3. maximum 16 of 16 

# THIS IS FOR EDUCATIONAL PURPOSES ONLY!!!!
# lacks security for the private keys 
# you'd want to use bip32 

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
		data = {'priv': random_key(), 'uncompressed': {}, 'compressed': {} }
		data['uncompressed']['wif'] = encode_privkey(data['priv'], 'wif')
		data['compressed']['wif'] = encode_privkey(data['priv'], 'wif_compressed')
		for c in ('compressed', 'uncompressed'):
			data[c]['pub'] =  privtopub(data[c]['wif'])
		myarray.append(data)
	return (myarray)

# make key pairs
print 'Making {} key pairs'.format(maxsigs)
keypairs = returnkeys(maxsigs)

# make the multi sig script and address
print("Making {} of {} multisig address".format(minsigs, maxsigs))
multisig_redeem_script = mk_multisig_script([p['compressed']['pub'] for p in keypairs], minsigs, maxsigs)

multisig_address = scriptaddr(multisig_redeem_script) # main net
testnet_multisig_address = scriptaddr(multisig_redeem_script, 196) # testnet

# print results
print("btc   : {}".format(multisig_address))
print("tbtc  : {}".format(testnet_multisig_address))
print("redeem: {}\n".format(multisig_redeem_script))
#for k in keypairs:
for i in range(len(keypairs)):
	print "prv{}: {}".format(i+1, keypairs[i]['priv'])
	print "pub{}: {}".format(i+1, keypairs[i]['compressed']['pub'])
	print "wif{}: {}".format(i+1, keypairs[i]['compressed']['wif'])
