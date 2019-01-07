# asset-man: Initialisation

This document describes the steps required to set-up and initialse the token issuance process and permissions on an Ocean federated blockchain. 

Prerequisites: 

* The amap library is installed and/or available in the path of the directory where the scripts are run
* The Ocean client is available locally or via an RPC connection
* An S3 remote file storage bucket is available and configured

### Controller Set-up

The first part of the initialisation involves the generation of the controller key pairs and the generation of the policy asset P2SH address and redeem script. For demonstration purposes, the single script `controller_setup.py` automatically generates 3 controller key-pairs and generates the corresponding 2-of-3 P2SH address and redeem script (which is saved to a file named `p2sh.json`). 

The script must be configured with the following parameters to enable a connection to the ocean client: `rpcport`, `rpcuser`, and `rpcpassword`. 

This script is run with:

`python3 controller_setup.py`

This script outputs the private key, public key and recovery phrase of each three controllers to screen, and writes each controller private key to a file `cX_privkey.dat`. The three controller public keys are added to a `ConPubKey` object, which is then written to the `controllers.json` file (this file is used for the mapping object signature verification). 

In the production version, each controller key-pair will be generated separately on isolated hardware. The private key will be stored on the isolated machine, and the recovery phrase written down by each controller to be stored securely. The public key for each controller will then be exported via removable media and sent to a single entity (CB) where they will be used to create the `controllers.json` and `p2sh.json` files. 

### Sidechain configuration


### Policy asset UTXO list


### Mapping initialisation

