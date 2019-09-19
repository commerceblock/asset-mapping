# asset-man: Token issuance protocol

This document describes the procedure for issuing a new mapped token on a controller-permissioned Ocean blockchain. It is assumed that the full initialisation process has been completed, as described in [initialisation.md](initialisation.md) and there are three controllers. Each controller has generated a secure and backed-up private key (stored on isolated hardware), and also has access to a workstation/PC that:

1. Has a full internet connection 
2. Has both Python3 and the `amap` library (and dependencies) installed 
3. Has a configured and synced Ocean client installed and running 
4. Has configured permissions for read/write access to an S3 remote filestore 
5. Has the controller public key file `controllers.json` in the local directory. 

The default policy of the issuance is configured as 2-of-3: this means that only 2 of the 3 controllers are required to issue new tokens and modify the mapping object (the third controller is only required if one of the first two controller keys is lost). One controller is designated as the _coordinator_ that initiates the issuance process, and the other is designated as the _confirmer_ that completes the issuance process. The proceedure is then detailed in terms of these two roles. 

### Coordinator

The coordinator runs the script `issue_token_coordinator.py` which must be configured with the following parameters:

1. The S3 bucket name in the `boto3` calls (default: `gtsa-mapping`)
2. The Ocean node RPC details: `rpcuser`, `rpcpassword` and `rpcport`
3. The reissuance token address `reissuanceToken`

`reissuanceToken` is the base-58 encoded address that the re-issuance token for each issuance is sent to - which enables to re-issuance (inflation) of the issued token. This address should be the P2SH multisig address of the block-signing federation script (which issues new tokens as part of the inflation/demurrage schedule). 

Once configured, the script is run as follows:

`python3 issue_token_coordinator.py`

The script is user-friendly and prints verbose verification information to screen. The current valid mapping object is retrieved from the S3 bucket and the signatures verified against the controller public keys. 

Details of the issuances (including asset details and issuance destination addresses) are entered via standard input. The controller private key (as generated at initialisation) must be in the file `c1_privkey.dat` located in the local directory. [Note that in production, the signing step will occur on a separate isolated device requiring a splitting of the script]. 

If the script completes without error, it produces two files which are written to the local directory: the partially signed updated mapping object `ps1_map.json` and the partially signed issuance transaction(s) `ps1_tx.json`. These files are automatically uploaded to the remote S3 bucket. 

### Confirmer

The confirmer runs the script `issue_token_confirmer.py` which must be configured with the following parameters:

1. The S3 bucket name in the `boto3` calls (default: `gtsa-mapping`)
2. The Ocean node RPC details: `rpcuser`, `rpcpassword` and `rpcport`
3. The reissuance token address `reissuanceToken`

Once configured, the script is run as follows:

`python3 issue_token_coordinator.py`

The script retrieves both the current _valid_ (i.e. fully signed) mapping object and the _new_ partially signed mapping object from the remote S3 repository, verifies the signatures and then displays the differences. The confirmer is required to verify that all of the issuances are correct and they then complete the issuance - the confirmer signatures are the partially signed issuance transactions. The issuance transactions are then broadcast to the network via the RPC interface with the Ocean node, and the script waits for confirmation before checking that all tokens have been issued on the blockchain correctly. 

Once blockchain issuance has been confirmed, the confimer signature is added to the partially signed mapping object making it valid and superseding the previous version (as it has a more recent timestamp and block-height). The new mapping object is written to file locally (`map.json`) and then automatically up-loaded to the S3 bucket. 

In addition, the `ptxo.dat` policy asset output database file is updated with the change in outputs and uploaded to the S3 bucket. 
