# asset-man

asset-man is a Python 3 library and set of associated scripts/utilities developed to manage the issuance, redemption, mapping and monitoring of tokenised assets on an Ocean blockchain. The core mapping library functions are independent of the blockchain client interface, but the _action_ scripts are designed to interface with the Ocean client RPCs. 

The library creates and manages a _mapping object_ which contains the cannonical mapping of on-chain token IDs to real-world asset references, and which forms a central part of the definition of the ownership of an asset (along with proof of ownership of the blockchain tokens via output private keys). 

## Requirements

In addition to Python 3.* the following libraries are required:

- Pybitcointools 
- Trezor's mnemonic implementation
- DataDiff

## Installation

To install the core mapping library

`$ git clone https://github.com/commerceblock/asset-mapping`
`$ cd asset-mapping`
`$ python setup.py install`

## Core library structure

The core library is located in the amap module. This module contains functions for key generation and recovery, and the MapDB class that operates on the mapping object. 