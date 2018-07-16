# Ocean Asset issuance and mapping protocol specification























This document describes the technical specification of the architecture and protocol for the 
issuance and redemption of tokenized assets on an Ocean federated sidechain. The specification 
is presented as a general framework, with clearly defined interfaces with the processes that 
will be unique to a particular asset custodian. 

The protocol is centred on a data structure (the mapping database or mapping object) that links 
tokens created within an Ocean blockchain to the custodians of a particular asset - as such it 
is a central part of the definition of the legal ownership of that particular asset, along with 
the ownership of the corresponding token output public key on the blockchain. The mapping database 
is then the link between the blockchain and the ‘real world’. 

## Mapping database

To define legal ownership, the mapping database must be accessible by token holders, and in the 
interests of transparency it should be as accessible as the sidechain itself (although this is not 
necessarily a requirement). However, the mapping can only be defined by the issuer (and custodian) 
of an asset - therefore the permissions to add to or modify the database must be clearly defined 
and controlled. 

The mapping database must be persistent and consistent - at any point in time the database must 
have a global state which reflects the legal ownership of the physical asset. A single state of 
the database can be enforced via a regular commitment to the Ocean sidechain, the immutability of 
which is enforced via q mainstay to the Bitcoin blockchain. This can be a part of the sidechain 
consensus layer, e.g. the hash of the mapping object can be included in the sidechain block header, 
which guarantees immutability. User wallets can confirm the authenticity of the mapping object 
via an SPV proof mechanism. 

The mapping database will provide the canonical link between asset IDs on an Ocean sidechain and 
physical assets. Asset IDs on Ocean are generated with on-chain entropy, and cannot be specified 
by the issuer - therefore the asset issuance process will require adding the generated asset IDs 
back into the database. If reissuance is not required, then the mapping signatories must confirm 
that the issuance transaction was flagged as non-reissuable (via an SPV proof) before authorising 
the issuance. If reissuance is required, the reissuance token becomes under the control of the 
issuing wallet - they key controlling the issuance token output then becomes a critical point of 
failure (i.e. whoever has this key can re-issue more of a valid asset). In this case, the issuance 
(and the issuing wallet) should be controlled by the authorised parties of the asset custodian 
(i.e. have the same permissions and security model as the mapping database modification permissions). 

## Mapping object

The mapping database will be stored and retrieved as a JSON object, with entries that consist of 
attribute-value pairs that link asset-IDs (blockchain generated) to asset identifiers (physical assets) 
and other metadata. The basic structure is outlines in the following example:

```json
{
  "date": "Thu 12 Jul 2018 12:27:51"
  "assets": [
    {
      "assetid": "78214125442A472D4A614E645267556B58703273357638792F423F4528482B4D",
      "amount": 402.342313
      "vref": "b87493"
      "location": "vault03 row18 shelf4"
      "issuer": "Acme"
    },
    {
      "assetid": "5468576D5A7134743777217A25432A462D4A614E645266556A586E3272357538",
      "amount": 399.573843
      "vref": "b45010"
      "location": "vault03 row12 shelf2"
      "issuer": "Acme"
    },
    {
      "assetid": "77397A24432646294A404E635166546A576E5A7234753778214125442A472D4B",
      "amount": 400.765738
      "vref": "b02361"
      "location": "vault02 row07 shelf4"
      "issuer": "Acme"
    }
  ],
  "signatures": [
    {
      "authkey": 1,
      "r": "404D635166546A576D5A7134743777217A25432A462D4A614E645267556B5870",
      "s": "A13F4428472D4B6150645367566B5970337336763979244226452948404D6251"
    },
    {
      "authkey": 3,
      "r": "3B7638792F423F4528482B4D6250655368566D597133743677397A2443264629",
      "s": "C14E645267556B58703273357538782F413F4428472B4B6250655368566D5971"
    }
  ]
}
```

The JSON object is composed of three components, the time/date, the asset list and the 
signatures. The signature attribute contains the required signatures to validate the asset 
mapping against the published public keys of the asset issuer and the authorisation policy 
(e.g. the signatures of 2 of 3 keys are required to authenticate the mapping). The signatures 
are generated over the hash of the asset list and time/date. The public keys of the asset 
issuance authorisers are published, and can be included in (or referenced from) the genesis 
block of the asset sidechain. 

## Protocol

### Initialisation of controllers

The controllers are the individuals/parties authorised to create and modify the mapping database. 
They would typically be appointed by the custodians of the physical assets, and the modification 
policy would be decided by the asset issuer. 

There could be a single controller, however they would have complete control and responsibility 
over the issuance of tokens and the mapping - if they were to lose the signing key, no more assets 
could be issued without a network wide hard fork to all wallet and node software. A more secure 
policy would be to require an n of m multi-signature modification rule: i.e. there are m controllers 
and at least n must add their signatures to the object to modify the mapping. A typical policy may 
be a *2-of-3* or *3-of-5* multisig, allowing for 1 or 2 controllers losing their keys or being unavailable. 

The m controllers are chosen by the issuing authority - these may be parties involved in verifying the 
deposits of physical assets (e.g. in a vault), and parties with legal responsibility for the security 
of the physical assets. In a ‘ceremony’ before the launch of the asset-backed sidechain, each of the 
controllers will generate a random private key *ski* (*i = 1, ..., m*) on an isolated piece of secure 
hardware (this could be an air-gapped PC, a hardware wallet or HSM). This key will then be used 
to generate a corresponding controller public key *pki = ski xG* (*G* denotes multiplication of the 
generator point on the secp256k1 elliptic curve). 

One (or *n*) of the controllers will have access to the Ocean sidechain wallet to which the issued 
asset will be sent. This wallet will then have ownership of the issued tokens, and the access 
policy will need to be decided upon by the issuers (e.g. this may be a multi-sig wallet). This 
wallet will have a direct (non-firewalled) connection to the sidechain signing nodes to enable 
it to create new sidechain assets. 

### Asset issuance

The proposed asset issuance protocol is as follows, where we assume that there is no re-issuance. 

1. At least *n* controllers agree that a physical asset is secured and that a token can be issued. They also agree on the issuer reference (serial number etc.), the mass of the asset and other data related to the issuance. 
2. Once agreement is reached, the controllers access the sidechain wallet and issue the tokenised asset (with an amount corresponding to the mass of the asset) using the `issueasset` wallet RPC. This will create and send the asset issuance transaction to the sidechain signing nodes, and return the 256 bit asset ID (which is randomly generated) and the transaction ID (TxID). 
3. Each of the *n* controllers must then confirm that the issuance transaction has been confirmed in a sidechain block and that the asset ID and token amount are correct. 
4. The mapping entry is then added to the JSON mapping object, along with the current time/date and then the *n* controllers add their digital signatures (ECDSA) to the object to authenticate it. 
5. The JSON object is then uploaded to a pre-defined repository (issuer server, IPFS) where it is accessible via a public API. 
6. The block-signing nodes retrieve the current JSON object, and verify the signatures against the published public keys and that the time/date supersedes the previous version. The SHA256 hash of the object is then added to the sidechain block header at every subsequent block. 

The token is then issued, and is owned by the controller wallet. It may then be transacted peer-to-peer natively on the sidechain. 

### Asset redemption

Physical assets can be redeemed by destroying the corresponding token, which is performed as follows:

1. A token holder signals to the asset issuer/custodian that they wish to redeem a specified amount of a particular token, which they send to the controller wallet (the controller will provide them with a redemption address). 
2. Once the controller wallet has received the token amount to be redeemed, it is destroyed using the `destroyamount` wallet RPC, which returns the destruction transaction ID. 
3. At least *n* controllers then agree that an amount X of the given asset ID has been destroyed, by independently verifying and inspecting the TxID. 
4. The entry in the mapping object corresponding to the destroyed token is then modified (either by reducing the mass by the equivalent token amount destroyed, or removing the entry if the entire asset is redeemed). The date/time is updated. 
5. Each *n* controllers then authenticate the change and add their signatures. 
6. The new signed JSON object is then uploaded and retrieved by the sidechain signing nodes. 
7. The corresponding asset (or part of it) is delivered to the redeemer by the custodian. 

### Asset re-mapping

The asset issuer may wish to reserve the right to change the mapping of physical assets to sidechain 
asset IDs for operation reasons. If different issued asset tokens have equivalent and indistinguishable 
value (e.g. they represent different units of the same precious commodity) then re-mapping may 
simplify the logistics of redemption and collection. An example of this is where an individual 
may hold in their wallet several fragments of different tokens that each represent units of a 
single commodity (each a separate asset) and that they wish to redeem the total amount of that 
commodity. In this case it would add significant additional cost to physically dissect several 
commodity units into fragments and then deliver a number of fragments to the redeemer. 
In this case, remapping can enable the individual to redeem the equivalent mass of a single 
unit. The re-mapping procedure (or shuffling procedure) is described as follows:

1. In the current mapping object, there are N asset mapping entries. Each entry has a mass mi of physical asset reference Ai mapped to a sidechain asset ID IDi (where i=1, ..., N). There are ai=mi tokens issued on the sidechain for each asset ID IDi. 
2. A token holder has *k* tokens of asset IDs *IDj* with values *xj* where *j = 1, ..., k*  
3. The token holder sends these k tokens to the controller wallet. 
4. The controller destroys each token amount *xj* of *IDj* (with the `destroyamount` wallet RPC). 
5. The asset IDs are then re-mapped:
   - The total amount (*xt*) of the fragments is calculated. 
   - Of all the *N* listed asset mappings, the one with the smallest mass which is greater than *xt* is identified (*As*). 
   - The mass of *As* is reduced by *xt:  ms <- ms-xt* (*xt* of *As* is then delivered to the redeemer). 
   - For each asset *Aj* (*j = 1, ..., k*) a new mapping is created, which links IDs to the assets corresponding to the destroyed tokens: *IDs <-> (Aj,m <- xj)*
   - For each mapping of asset *Aj* to *IDj* (*j = 1, ..., k*) the mass *mj* is reduced corresponding to the destroyed tokens (and the reallocated mass): *mj <- mj-xj* 

### Asset map object usage

The mapping JSON object will be available via a public API. A sidechain asset SPV wallet will retrieve 
the object and verify the signatures against the controller public keys and policy. The SPV wallet 
then confirms that the object is unique by checking the hash of the object against the sidechain block header. 
