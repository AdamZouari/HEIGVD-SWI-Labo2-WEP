
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


def encryption(fragment, arp ,key = '\xaa\xaa\xaa\xaa\xaa'):
    
    # on calcule le icv (A.K.A CRC 32) et on le converti en unsigned int little-endian
    # To generate the same numeric value across all Python versions and platforms use crc32(data) & 0xffffffff.
    icv = binascii.crc32(fragment) & 0xffffffff  
    icv_clair = struct.pack('<I', icv)
    
    # on ajoute l'icv au fragment pour le donner en input de RC4
    fragment_clair = fragment+icv_clair
    
    # on garde la meme seed
    seed = arp.iv + key
    
    # chiffrement rc4
    return rc4.rc4crypt(fragment_clair,seed)

# methode qui fragmente et chiffre un message de taille quelconque en fragments de 36 caracteres
def fragment_and_encrypt(message):
    
    nb_fragment = int(math.ceil(len(message)/36.))
    fragmented_message = nb_fragment * [""]
    encrypted_fragments = len(fragmented_message) * [""]
    trames = []
    
    
    i = 0
    while i < len(fragmented_message):
        
        # On recupere le paquet fourni
        arp = rdpcap('arp.cap')[0]
    
        # si premier fragment
        if i == 0:
            fragmented_message[i] = message[0:36]
            
        # pour les autres fragments, on update le compteur de fragments
        else:
            fragmented_message[i] = message[i*36: (i+1)*36]
            arp.SC = i
            
        # si il reste encore des fragments, alors on set le bit More Fragment a 1 (3e bit de poids faible de FCfield)
        if i != len(fragmented_message) -1:
            arp.FCfield = arp.FCfield | 0x4
        
        # si fragrement trop petit on ajoute du padding
        if len(fragmented_message[i]) < 36:
            fragmented_message[i] = fragmented_message[i] + ' '*(36 - len(fragmented_message[i]))
        
        # chiffrement du fragment
        encrypted_fragments[i] = encryption(fragmented_message[i], arp)
        
        # on recupere le icv chiffre (4 derniers bytes) et le convertit en Long big endian
        (icv_num,) = struct.unpack('!L', encrypted_fragments[i][-4:])
        
        # on met a jour le icv ainsi que le message chiffre
        arp.icv = icv_num
        arp.wepdata = encrypted_fragments[i][:-4]
        
        # on ajoute chaque paquet fragmente au tableau de fragment
        trames.append(arp)
        
        i += 1
    
    # on cree un fichier pcap pour tout ces fragments
    wrpcap('arpv2-frags.cap', trames)
    
    print " DONE "     

   

#Cle wep AA:AA:AA:AA:AA
#key='\xaa\xaa\xaa\xaa\xaa'



# creation du message a chiffre (multiple de 36) et stockage dans un tableau de string contenant les fragments
message = "Salut Adaaaaaaaaaaaaaaaaaaaaaaaaaam Salut Naaaaaaaaaaaaaaaaaaaaaaaaaair Salut Abrahaaaaaaaaaaaaaaaaaaaaaaaam"
message2= "helloooooooooooooooooooooooooooooooooooooooooooooooooo"

fragment_and_encrypt(message)



