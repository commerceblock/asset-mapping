# asset-man: Asset redemption protocol

This document describes the procedure for redeeming an asset backed mapped token on a controlled Ocean blockchain. It is assumed that the full initialisation process has been completed, as described in [initialisation.md](initialisation.md) and there are two available controllers (coordinator and confirmer). It is assumed that tokens have been issued, and that a _redeemer_ has sufficient tokens to redeem and asset. 

The redemption process is dependent on a list of _redeemable_ assets: this is a simple JSON array of asset references that can be redeemed and is a subset of all issued assets. The redeemable asset list is stored in a file `rassets.json` which is uploaded to the S3 bucket. The redemption process involves four entities (redeemer, custodian, coordinator and confirmer), which perform operations in the following sequence:

### Redeemer

The redeemer wishes to redeem one of the assets listed in the `rassets.json` object (these can be displayed on the redemption website). The script `get_redeemable.py` displays the current list, along with the amount of tokens required to redeem each of the listed assets (which is a function of the asset quantity and the current token ratio). 

The redeemer then chooses an asset to redeem and runs the `freeze_script.py` (after configuring `rpcuser`, `rpcpassword` and `rpcport` to their local Ocean wallet). This script prompts them to enter the reference ID of the asset they have chosen to redeem. The script then interacts with the redeemer wallet to generate a signed _redemption transaction_ that is exported as a file: `rtx-assetid.dat` (where `asset` is the asset reference). This transaction pays the exact quantity of tokens (of any number and type of token ID) to redeem the asset at the current token ratio, back to addresses controlled by the redeemer wallet. In addition, the first output of the transaction consists of zero value paying to a _zero_ address (i.e. `0x0000000000000000000000000000000000000000`) which tags the redemption transaction as _uninflatable_ to the signing nodes. Note that the redemption transaction has not been broadcast at this point. 

In addition to the redemption transaction, the redeemer must also pay a _redemption fee_ in tokens. The fee amount `rfee` is displayed on the redemption website, along with custodian fee address (`fAddress`). The redeemer generates an additional raw transaction from their wallet paying the fee to this address, using any tokens, which is exported into a file `rfee.dat`. 

The redeemer then initiates the redemption of the asset by sending a request to the _custodian_ (via a web-interface) which included the two raw transaction files. 

### Custodian

The custodian is the general term for the entity processing the redemption and the delivery of the asset to the redeemer. The redemption request to the custodian (via a web-interface) then must specify the asset reference ID, and include the `rtx-assetid.dat` and `rfee.dat` transaction files (uploaded as attachments). [the request may include additional user information and delivery information]. 

The custodian (back-end, with connection an Ocean node) then performs the following operations:

1. Check the redemption fee tx is valid (and pays to the correct custodian address)
2. Check that the asset reference is in the `rassets.json` array. 
3. Decode the raw transaction contained in the `rtx-assetid.dat`
4. Check that the transaction is valid
5. Check that the total tokens transfered in the transaction equal the asset quantity multiplied by the current token ratio. 
6. The asset reference in the `rassets.json` array is marked as _locked_ and the file is uploaded to the S3 bucket. 

Once validity is confirmed, the transactions are submitted after the redeem transaction addresses are added to the freezelist. 

1. Submit fee transaction
2. Add redemption transaction output addresses to freezelist
3. Confirm freezelist
4. Submit the redemption transaction to the network
5. Confirm - send transactions IDs to the custodian back-office (via e-mail). 

This logic is implemented in the `redeem_check.py` script. 

### Redeemer

The redeemer is contacted directly by the custodian with further instructions. If the redemption request is not accepted, the custodian updates the freezelist database to remove the redemption transaction output addresses. These become spendable again and the redeemer can spend those outputs. 

If the redemption request is accepted, the custodian adds the output addresses to the _burnlist_ database. This then enables to the redeemer to submit a _burn_ transaction spending the outputs of the redemption transactions to NULL (OP_RETURN) outputs. 

To do this, the redeemer runs the `burn_tokens.py` script (after configuring `rpcuser`, `rpcpassword` and `rpcport` to their local Ocean wallet). This script requires the user to enter the txid and vout indexes of the redemption transaction. The script then outputs the token IDs and values that have been burnt to the file `burntassets.dat`, which is sent by the redeemer to the custodian (via email etc). 

### Custodian

The custodian receives the `burntassets.dat` from the redeemer, along with the burn transaction txid. The custodian then checks that burn transaction is confirmed, and the redeemer takes possession of the asset. The custodian then contacts the controllers (and sends them the `burntassets.dat` file) to finalise the re-mapping of the mapping object. 

### Coordinator

The coordinator runs the script `redemption_coodinator.py` which requires the input of the data in the `burntassets.dat` file. The script automatically checks that the tokens are burnt on the blockchain and then removes the redeemed asset from the mapping object, remapping the associations if required. 

The partially signed updated (re-mapped) object is uploaded to the S3 bucket. 

### Confirmer

The confirmer runs the script `redemption_confirm.py` which again requires the input of the data in the `burntassets.dat` file. The script automatically checks that the tokens are burnt on the blockchain, and verifies the changes in the re-mapped object, before adding the controller signature and uploading the fully signed and re-mapped object to the S3 bucket, completing the redemption process. 