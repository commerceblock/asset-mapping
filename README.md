# asset-man

asset-man is a Python 3 library and set of associated scripts/utilities developed to manage the issuance, redemption, mapping and monitoring of tokenised assets on an Ocean blockchain. The core mapping library functions are independent of the blockchain client interface, but the _action_ scripts are designed to interface with the Ocean client RPCs. 

The library enables the creation and management of a _mapping object_ which contains the cannonical mapping of on-chain token IDs to real-world asset references, and which forms a central part of the definition of the ownership of an asset (along with proof of ownership of the blockchain tokens via output private keys). 

## Requirements

In addition to Python 3.* the following libraries are required:

- Pybitcointools 
- Trezor's BIP39 mnemonic implementation
- DataDiff
- Boto3 for Amazon S3 (remote mapping object storage)

## Installation

To install the core mapping library

`$ git clone https://github.com/commerceblock/asset-mapping`

`$ cd asset-mapping`

`$ python setup.py install`

## Core library structure and API

The core library is located in the amap module. This module contains functions for key generation and recovery, and the `MapDB` class that operates on the mapping object. 

The library contains the following functions:

`controller_keygen()`

Returns a random, securely generated 32 byte private key, a correspondoing compressed secp256k1 EC public key and a 12 word BIP39 recovery seed phrase. 

`controller_recover_key(recovery_phrase)`

Returns the 32 byte private key and correspondoing compressed secp256k1 EC public key when passed a 12 word BIP39 recovery seed phrase. 

`token_ratio(blockheight)`

Returns the token to asset ratio at the supplied blockheight. This function is hard-coded with the initial token to asset ratio and the inflation rate as a function of block height. 

A mapping object is instantated with the `MapDB` class, and the constructor is optionally passed the n-of-m multisig policy (default 2-of-3). The mapping object is internally handled as a dictionary object and writen to file as a JSON object. 

The object has the following methods:

Method | Description
--- | ---
`add_asset(asset_ref,year_ref,mass,tokenid,manufacturer)` | Create a new entry in the mapping object: `asset_ref`, `year_ref` and `manufacturer` define the full asset reference, `mass` is the amount of asset and `tokenid` is the Ocean generated 32 byte token ID. 
`update_time(ntime)` | Set the mapping object timestamp (seconds since UNIX epoch). If no argument is given, the current system time is used. 
`update_height(blockheight)` | Set the blockheight stamp in the mapping object. 
`get_time()` | Return the current object timestamp
`get_height()` |  Return the current object block height. 
`remove_asset(asset_reference)` | Remove all assets from the object with the supplied asset reference. 
`verify_multisig(controller_pubkeys)` | Verify the object ECDSA signature against the object multisig policy. `controller_pubkeys` is a list of the hex encoded (compressed) controller public keys. Returns either `True` or `False`. 
`verify_blockchain_commitment(commit)` | Verify the SHA256 hash of the entire object against the supplied value. Returns either `True` or `False`. 
`load_json(filename)` | Load a JSON encoded object from file. `filename` is the file path. 
`sign_db(privkey,index)` | Add an ECDSA signature to the object, using a hex encoded 32 byte private key `privkey`. `index` is used to specify the private key owner (i.e. the controller number). 
`export_json(filename)` | Export the object to a JSON encoded file. `filename` is the file path.
`print_json()` | Prints the JSON encoded object to screen. 
`remap_assets(burnt_tokens,asset_reference,redemption_height)` | Remap the assets in the object as an arbitrary number of tokens are destroyed to redeem a single asset. `burnt_tokens` is an array of the token IDs that have been burnt and the corresponding amounts. `asset_reference` is the full reference of the asset that is being redeemed. `redemption_height` is the blockchain height at which the redemption was initiated. Returns `True` if successful, or `False` with an error message if the re-mapping fails due to incorrect supplied values. 
`get_total_mass()` | Returns the total amount of all assets in the mapping object. 
`get_mass_tokenid(tokenid)` | Returns the total amount of assets mapped to `tokenid`. 
`get_mass_asset(asset_ref)` | Returns the total amount of `asset_ref`. 

## Scripts

The various scripts and utilities included in the repository perform various functions in the lifecycle of a mapped token, including asset issuance, the redemption process and the monitoring of tokens issued on-chain. These scripts interact with both a remotely stored mapping object and with the Ocean blockchain client via the RPC interface. 

The following operation scripts are included (in the `scripts` directory):

`object_init.py`

Creates an unsigned and empty mapping object `map.json` with a 2-of-3 signature policy and uploads it (and the policy asset output `ptxo.dat` file) to the S3 bucket. 

`controller_setup.py`

Securely generates controller public/private key pairs and BIP39 mnemonic seed phrases. It generates a `c_privkey.dat` file with the controller private key and prints the backup seed phrase to the terminal. It also can generate a `controllers.json` file which contains the public key(s) and a `p2sh.json` file which contains the mutlisig Ocean P2SH address and redeem script corresponding to the controller public keys (for multiple controllers with a 2-of-3 policy). 

`issue_token_coordinator.py`

Initiates the issuance of new tokens corresponding to controlled assets, performed by the _coordinator_. With a 2-of-3 policy, any one controller can be the coordinator and any other the _confimer_. The script retrives the mapping object and policy asset UTXO file from an S3 bucket and verifies the signatures. Issued asset details are input by the coordinator and the script generates a new partially signed mapping object `ps1_map.json` and partially signed issuance transaction `ps1_tx.json` which are uploaded to S3. `reissuanceToken` must be set to the address of the inflation controller (the block-signing federation). 

`issue_token_confirm.py`

Completes the issuance of new tokens, performed by the confirmer. The script retrieves parially signed mapping object and issuance transaction, and confirms the issuance details. The confirmer signatures are then added and the issuance transaction is broadcast to the network. Once confirmation is recieved, the fully signed mapping object is uploaded to S3. 







