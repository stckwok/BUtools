Bitcoin Unlimited [Website](https://www.bitcoinunlimited.info)  | [Download](https://www.bitcoinunlimited.info/download)


Bitcoin Unlimited Tools
=====================================

* [Emacs Environment](elisp/README.md)
* [Bitcoin CLI](btccli/README.md)
* [Transaction generation scripts](scripts.md)

Setup
====================

- git submodule init
- git submodule update
- cd pythonbitcoinlib/ && ./setup.py build


Example
====================
1. Install and start bitcoind in regtest mode

     ```
     $ bitcoind -regtest -daemon
     ```

2. Generate blocks with balance
     ```
     $ bitcoin-cli generate 101
     ```

3. Show blockchain headers
     ```
     $ ./chainExplorer.py regtest 20
     ```

4. Repeat step 1 to 3 with other modes with mining to generate blocks
     ```
     $ ./chainExplorer.py nol 20
     ```
