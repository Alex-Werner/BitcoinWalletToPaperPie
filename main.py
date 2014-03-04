from __future__ import print_function
import hashlib, binascii, ecdsa

sha256 = lambda h: hashlib.sha256(h).digest()
ripemd160 = lambda h: hashlib.new("ripemd160",h).digest()
md5 = lambda h: hashlib.md5(h).digest()

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)


# ----------------------------------#
#| Misc
# ----------------------------------#

def b58encode(v):
    n = long(v.encode("hex"), 16)
    r = ""
    while n > 0:
        n, mod = divmod(n, 58)
        r = __b58chars[mod] + r

    pad = 0
    for c in v:
        if c == '\x00':
            pad += 1
        else:
            break

    return (__b58chars[0] * pad) + r

def b58decode(v, length):
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += __b58chars.find(c) * (__b58base ** i)

    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    result = chr(long_value) + result

    nPad = 0
    for c in v:
        if c == __b58chars[0]:
            nPad += 1
        else:
            break

    result = chr(0) * nPad + result
    if length is not None and len(result) != length:
        return None

    return result



# ----------------------------------#
#| Crypto Inherents func
# ----------------------------------#

def getEcdsaPair():
    import ecdsa

    output = {}
    ecdsaPrivKey = ecdsa.SigningKey.generate(curve=ecdsa.curves.SECP256k1)
    ecdsaPubKey = ecdsaPrivKey.get_verifying_key()

    output['ecdsaPrivKey'] = ecdsaPrivKey.to_string()
    output['ecdsaPubKey'] = ecdsaPubKey.to_string()

    return output

# ----------------------------------#
#| Bitcoin Inherents func
# ----------------------------------#

def getBitcoinPairFromEcdsa():
    output = {}

    data = getEcdsaPair()

    bitcoinPrivKey = data['ecdsaPrivKey']
    bitcoinPubKey = "\x00" + ripemd160(sha256("\x04" + data['ecdsaPubKey']))
    checksum = sha256(sha256(bitcoinPubKey))[:4]
    bitcoinPubKey = bitcoinPubKey + checksum

    output['bitcoinPrivKey'] = bitcoinPrivKey.encode("hex")
    output['bitcoinPubKey'] = bitcoinPubKey.encode("hex")

    return output


def getB58BitcoinPairFromBitcoinPair():
    output = {}

    data = getBitcoinPairFromEcdsa()
    B58BitcoinPubKey = b58encode(data['bitcoinPubKey'].decode("hex"))
    B58BitcoinPrivKey = "\x80" + data['bitcoinPrivKey'].decode("hex")
    checksum = sha256(sha256(B58BitcoinPrivKey))[:4]
    B58BitcoinPrivKey = b58encode(B58BitcoinPrivKey + checksum)

    output['PrivateKey'] = B58BitcoinPrivKey
    output['PublicKey'] = B58BitcoinPubKey

    return output


# ----------------------------------#
#| W.I.P
# ----------------------------------#

def SearchForPattern(pattern):
    for i in range(100000):
        data = getB58BitcoinPairFromBitcoinPair()

        search = pattern
        pub = data['PublicKey']
        priv = data['PrivateKey']

        print(pub)
        if pub.find(search)==1:
            print("Yay! Found in "+i+" iterations PRIV:"+priv+"- PUB:"+pub)
            return 1

    return 0

def CrackPubKey(pubkey):
    return 0


def getBalanceFromBitcoinAdress(bitcoinadress):
    import urllib2
    #DO NOT EXCEED 1 request per 10sec = 6 request per second.
    balance = urllib2.urlopen("https://blockchain.info/q/addressbalance/"+bitcoinadress).read()
    #Divide by 100000000 to get BTC instead of satoshies

    return balance

# ----------------------------------#
#| Coded When Drunk Stuff : WHAT THE FUCK IS THAT ? TODO : Find why this is here !
# ----------------------------------#

def RunNotEmptyAdressFinder(iteration):
    import time

    start_time = time.time()
    interval = 2
    empty = 0
    notempty = 0

    for i in range(iteration):
        time.sleep(start_time + i*interval - time.time())



        data = getB58BitcoinPairFromBitcoinPair()
        readableTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


        balance = getBalanceFromBitcoinAdress(data['PublicKey'])

        if balance == "0":
            empty += 1
        else:
            notempty += 1

        string = "{'date':'"+readableTime + "','balance':'" + balance + "', 'private':'"+data['PrivateKey']+"', 'public':'"+data['PublicKey']+"'},"
        with open("test.txt", "a") as myfile:
            myfile.write(string)

        print(str(notempty)+"/"+str(empty))


# ----------------------------------#
#| COOOOOOOOORE (With growl, beers and stuff like that :o)
# ----------------------------------#

#If You want to create many wallet and check if they are not empty (Wich will never happen on a human life-time, well you can. )
#In fact, this is totally useless, but drugs & alcohol said that it wasn't sooooo i did...
#RunNotEmptyAdressFinder(10)

#Create a new bitcoin pair
print(getB58BitcoinPairFromBitcoinPair())

#Try to set a vanity adress [Do not mention the "1", do not forget the missing letters (l, I, 0, o)]
#SearchForPattern("t")