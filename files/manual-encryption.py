
#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

""" Manually decrypt a wep message given the WEP key"""

__author__      = "Alic Nair et Zouari Adam"
__copyright__   = "Copyright 2019, HEIG-VD"
__license__ 	= "GPL"
__version__ 	= "1.0"
__email__ 		= "nair.alic@heig-vd.ch et adam.zouari@heig-vd.ch"
__status__ 		= "Prototype"

from scapy.all import *
import rc4
import binascii


#Cle wep AA:AA:AA:AA:AA
key='\xaa\xaa\xaa\xaa\xaa'

# On recupere le paquet fourni
arp = rdpcap('arp.cap')[0]  

# creation du message a chiffre
message = "Salut Adaaaaaaaaaaaaaaaaaaaaaaaaaaam"

# on calcule le icv (A.K.A CRC 32) et on le converti en unsigned int little-endian
# To generate the same numeric value across all Python versions and platforms use crc32(data) & 0xffffffff.
icv = binascii.crc32(message) & 0xffffffff  
icv_clair = struct.pack('<I', icv)

# on ajoute l'icv au message pour le donner en input de RC4
message_clair = message+icv_clair

# on garde la meme seed
seed = arp.iv + key

# chiffrement rc4
ciphertext = rc4.rc4crypt(message_clair,seed)

print "ciphertext : " + ciphertext.encode("hex")
print "icv_encrypted : " + ciphertext[-4:].encode("hex")

# on recupere le icv chiffre (4 derniers bytes) et le convertit en Long big endian
(icv_num,) = struct.unpack('!L', ciphertext[-4:])

# on met a jour le icv ainsi que le message chiffre
arp.icv = icv_num
arp.wepdata = ciphertext[:-4]

wrpcap('arpv2.cap',arp)

