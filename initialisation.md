# asset-man: Initialisation

This document describes the steps required to set-up and initialse the token issuance process and permissions on an Ocean federated blockchain. 

Prerequisites: 

* The `amap` library is installed and/or available in the path of the directory where the scripts are run
* The Ocean client is available via an RPC connection
* An S3 remote file storage bucket is available and configured with write permissions for each controller (all scripts are configured for the bucket `gtsa-mapping`)

### Controller Set-up

The first part of the initialisation involves the generation of the controller key pairs and the generation of the policy asset P2SH address and redeem script. For demonstration purposes, the single script `controller_setup.py` automatically generates 3 controller key-pairs and generates the corresponding 2-of-3 P2SH address and redeem script (which is saved to a file named `p2sh.json`). 

The script must be configured with the following parameters to enable a connection to the ocean client: `rpcport`, `rpcuser`, and `rpcpassword`. 

This script is run with:

`python3 controller_setup.py`

This script outputs the private key, public key and recovery phrase of each three controllers to screen, and writes each controller private key to a file `cX_privkey.dat` (X = 1,2,3). The three controller public keys are added to a `ConPubKey` object, which is then written to the `controllers.json` file (this file is used for the mapping object signature verification). 

In the production version, each controller key-pair will be generated separately on isolated hardware (by running the script `controller_single.py`). The private key will be stored on the isolated machine, and the recovery phrase written down by each controller to be stored securely. The public key for each controller will then be exported via removable media (or written down) and sent to a single entity (CB) where they will be used to create the `controllers.json` and `p2sh.json` files (by running the script `controller_aggregate.py`). 

### Sidechain configuration

Once the controller public keys have been generated and aggregated, the Ocean blockchain can be configured with the controller public keys. This is done to immutably link the controllers with the blockchain (so that the mapping object signatures can be verified directly) and to pay the policy asset coins to a multisig controller address, which will give them permission to create new token types. 

The controller public keys are added to the `ocean.conf` file via the `issuecontrolscript` parameter. This parameter is set to the hex-encoding of the redeem script generated in the `p2sh.json` file. The `initialfreecoinsdestination` parameter is set with the P2SH multisig `scriptPubKey` generated in the `p2sh.json` file. In addition a quantity of policy asset coins to be generated in the genesis block must be specified (this value is arbitrary, but must be greater than 100) with the `initialfreecoins` parameter. For example:

```
initialfreecoins=50000000000000
initialfreecoinsdestination=a91469b4ee09eca516ae4c380b7f7e63a492340517bc87
issuecontrolscript=5221035cb05851130ee7aa09ca43dae988d36ab6b8dbb06dd3948295b919084056d4ce2103925c07cdc8b04b6f4ab84e6e120648d91517911d2a28decf9ad37cae333413a52102de3441f8a7ecb17417cc764143bda6f19ee5dc85de94534af5a411cd6ef12b5953ae
```

This configuration then forms part of the genesis block definition. 

### Policy asset UTXO list

In order to issue new tokens, issuance transactions (signed by the controllers) must spend a policy asset output. These outputs are initially created in the genesis block, and are tracked by the issuance process (i.e. new policy asset outputs are created as change for each issuance). The current list of available policy asset outputs is kept in the the `ptxo.dat` wallet file, which is updated at each issuance. 

To initialise the `ptxo.dat` wallet file, first determine all the policy asset outpoints by first importing the controller P2SH address into a configured Ocean client wallet:

`ocean-cli importaddress 3BKwcuph76AgTgo7d5nNdW4EYRL7v1PawN`

Then list all unspent outputs:

`ocean-cli listunspent`

For each output, add a line to the `ptxo.dat` file with:

`txid   vout   value`

### Mapping initialisation

Once the blockchain has been configured and initialised, a 'blank' and unsigned mapping object with a 2-of-3 policy is created and exported as a file: `map.json`. This blank object and the `ptxo.dat` wallet file are then uploaded to the S3 bucket. All these operations are performed by running the `object_init.py` script. 
