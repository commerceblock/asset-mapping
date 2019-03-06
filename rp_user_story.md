# Redemption process user stories

1. Token holder decides to redeem his tokens for a physical gold bar. 

2. Visits the GTSA website, and navigates to the redemption page. 

3. Follows instructions on the redemption page. 

4. The redemption page has a list of the gold bars that may be redeemed (maybe as a pop-up or drop down list). This list is generated from the file `rassets.json` (all _unlocked_ bars). The list also displays the `mass` of each of the bars in `rassets.json` along with `rtokens`, the amount of tokens currently required to redeem it. To determine the values `mass` and `rtokens` for each bar, the website back-end must reference the mapping table (`map.json` available via a public API) and a GTSA blockchain node (via an RPC connection, to get the current blockheight and calculate the corresponding gold-to-token ratio). 

5. The token holder notes the required tokens for the bar he wants to redeem, and the tokens required to pay the admin fee. 

4. The token holder opens his GTSA wallet. He selects the option to generate a redemption transaction. He enters the required tokens for his chosen bar. The wallet then generates and signs a redemption transaction for the required tokens. This raw transaction is then exported as a file. 

5. The tokens holder then selects a wallet option to generate a raw transaction for the admin fee amount and this is exported as a file. 

6. The token holder then goes back to the redemption website, enters his details and other info, selects the bar he wants to redeem, and uploads the two raw transactions exported from his wallet. 

7. The token holder submits the request (i.e. submits the web form). 

8. Immediately, the `rassets.json` file is modified to _lock_ the bar that the token holder has selected (to prevent others users from now selecting it). 

9. The two raw transactions are verified by the script `redemption_check.py`. This script connects to a GTSA blockchain node (via an RPC connection), and automatically checks the transactions, updates the freezelist and then submits the transactions. 

10. Once the transactions have confirmed (after 2 minutes), the user is notified (via the website and automated e-mail), and the user data and confirmed transaction IDs are sent (via an automated e-mail) to the GTSA office for off-line manual processing. 
