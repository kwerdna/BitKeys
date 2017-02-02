# many addresses from one pub key
import sys
from bitcoin import *
import base58

# from one private key you can create 2 bitcoin addresses
# one from the uncompressed public key and one from the compressed public key
# * also 2 addresses for each altcoin.

maxsigs = 3
if len(sys.argv) == 2:
	maxsigs = int(sys.argv[1])
	if maxsigs > 16: maxsigs = 16;
 
def returnkeys(n):
	myarray = []
	for i in range(n):
		data = {'priv': random_key()} 
		# the encoding of the private key indicates the desired public key format
		data['uncompressed'] = {'wif': encode_privkey(data['priv'], 'wif')}
		data['compressed'] = {'wif': encode_privkey(data['priv'], 'wif_compressed')}
		for c in ('compressed', 'uncompressed'):
			# public key will be compressed or uncompressed based on the wif format 
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
		for s in ('wif', 'pub', 'btc', 'tbtc', 'ltc', 'doge', 'tdoge', 'dash', 'tdash'):
			print ("    {}:\t{}".format(s, key[c][s]))
	print "=*=" * 10 

