#!/usr/bin/env python2
import sys, pdb
import bitcoin
import helpers.rpc as rpc
import bitcoin.core
import bitcoin.wallet
import time
import types
import datetime
from decimal import *
import httplib
import socket
import random

from helpers.buHelpers import *
HOST_IP = "10.54.150.74"
#HOST_IP = "localhost"
HOST_PORT = 19011

#bitcoin.SelectParams('testnet')
bitcoin.SelectParams('regtest')

BTC = 100000000
mBTC = 100000
uBTC = 100

DEFAULT_TX_FEE = 10000

PerfectFractions = True

cnxn = None

# 60sec/min * 10 min
BLK_GENERATION_INTERVAL = 600

#op_lists = ["unspent", "join", "spamtill", "spam", "sweep", "split", "info"]

def main(op, params=None):
  global cnxn
  print("Parameters : ", params)
  #cnxn = rpc.Proxy()
  #cnxn = rpc.Proxy2("http://10.54.150.74", 19011)  # Ub-test

  try:
    if params is not None and "localhost" in params:
        print("Local Proxy ...")
        cnxn = rpc.Proxy()
    elif [True for txt in params if "ipaddress=" in txt]:
        print("IP Address is input ...")
        ip, port = find_params("ipaddress=", params)
        #print(ip, port)
        if validip(ip):
            print("IP Address is validated ...")
            cnxn = rpc.Proxy2("http://" + ip, port)
    elif validip(HOST_IP):
        print("Default IP Address and Port ...")
        cnxn = rpc.Proxy2("http://" + HOST_IP, HOST_PORT)  # Ub-test
  except ValueError as err:
    print str(err)
    #pdb.set_trace()
    sys.exit(1)

  try:
    print (cnxn.getbalance())
  except ValueError as v:
    print str(v)
    pdb.set_trace()
  try:
    print (cnxn.getbalance())
  except ValueError as v:
    print str(v)
    pdb.set_trace()

  addrs = [cnxn.getnewaddress(),cnxn.getnewaddress()]
  change = [cnxn.getrawchangeaddress()]

  #wallet = cnxn._call("listreceivedbyaddress")
  #wallet = cnxn._call("listunspent")
  if op=="unspent":
    wallet = cnxn.listunspent()
    if wallet:
        print ("This wallet has %d unspent outputs." % len(wallet))
        #print (" Wallet has : " , str(wallet[0]))

  if op=="join":
    if len(params):
      amt = int(params[0])
    else:
      amt = 100
    if len(params)>2 and isLocalHost(params) is False and [True for txt in params if "ipaddress=" in txt] == []:
      repeat = int(params[1])
    else:
      repeat = 1

    wallet = cnxn.listunspent()
    # print "This wallet has %d unspent outputs.  Joining the %d at offset %d." % (len(wallet),amt, offset)
    # consolidate(wallet[offset:offset+amt],cnxn.getnewaddress(), cnxn)
    print ("This wallet has %d unspent outputs.  Joining %d, %d times." % (len(wallet),amt, repeat))
    offset = 100
    for cnt in range(0,repeat):
      print (cnt)
      bigAmt = wallet[0]
      itr = 0
      idx = 0
      for tx in wallet:  # Find a larger utxo that will pay for a lot of dust
        if tx["spendable"] is True and bigAmt["amount"] < tx["amount"]:
          bigAmt = tx
          idx = itr
        itr += 1
      del wallet[idx]
      print (str(bigAmt))
      consolidate(wallet[offset:offset+amt] + [bigAmt],addrs[0], cnxn)
      del wallet[offset:offset+amt] # delete all the entries I just used
      offset+=amt
      if offset > len(wallet): break

  #wallet = cnxn.listunspent()
  #addrs = [cnxn.getnewaddress() for i in range(0,10)]
  #split([wallet[0]],addrs, cnxn)
  if op=="spamtill":
    if len(params):
      poolSize = int(params[0])
    else:
      poolSize = None
    amt = None
    addrs = [cnxn.getnewaddress() for i in range(0,25)]
    while 1:
      try:
        spamTx(cnxn,50000,addrs, amt,False,mempoolTarget=poolSize)
      except rpc.JSONRPCError as e:
        print ("Out of addresses.  Sleeping")
        time.sleep(60)
      except httplib.BadStatusLine as e:
        cnxn = rpc.Proxy()
      except (socket.error,socket.timeout) as e:  # connection refused.  Sleep and retry
        while 1:
          try:
            time.sleep(30)
            cnxn = rpc.Proxy()
            break
          except:
            pass

  if op=="spam":
    if len(params):
      amt = int(params[0])
    else:
      amt = None
    addrs = [cnxn.getnewaddress() for i in range(0,25)]
    while 1:
      try:
        spamTx(cnxn,50000,addrs, amt,False)
      except rpc.JSONRPCError as e:
        print ("Out of addresses.  Sleeping")
        time.sleep(60)
      except httplib.BadStatusLine as e:
        cnxn = rpc.Proxy()
      except (socket.error,socket.timeout) as e:  # connection refused.  Sleep and retry
        while 1:
          try:
            time.sleep(30)
            cnxn = rpc.Proxy()
            break
          except:
            pass

  if op=="sweep":
    wallet = cnxn.listunspent()
    offset = 100
    spend = []
    while len(spend) < 10:
      if not wallet:
        break
      tx = wallet[0]
      del wallet[0]

      if tx["spendable"] is True and tx["amount"] < 100000 and tx["confirmations"] > 0:
        print (str(tx))
        spend.append(tx)

    if spend:
      consolidate(spend,cnxn.getnewaddress(), cnxn,5000*len(spend))
    else:
      print ("there is nothing to sweep")

  if op=="split":
    if len(params):
      nSplits = int(params[0])
    else:
      nSplits = 25
    if len(params)>1 and isLocalHost(params) is False and [True for txt in params if "ipaddress=" in txt] == []:
      fee = int(params[1])
    else:
      fee = 9000

    wallet = cnxn.listunspent()
    j = 0
    addrs = [cnxn.getnewaddress() for i in range(0,nSplits)]
    for w in wallet:
      j+=1
      if w['amount'] > nSplits*BTC:
        if 1: # try:
          print("\n ... [w] = ", [w])
          split([w],addrs, cnxn, fee)
          print ("split %d satoshi into %d addrs fee %d %s" % (w['amount'],nSplits, fee, str(addrs)))
        else:  # :except rpc.JSONRPCError as e:
          print ("\n%d: Exception %s" % (j,str(e)))
          pdb.set_trace()
      else:
        print ("address has only %d satoshi" % w['amount'])
      # else: print "Split: %d" % j

  if op=="info":
    blkid = cnxn.getbestblockhash()
    blk = cnxn.getblock(blkid)
    txn = blk.vtx[0]
    print (txn.vin)
    print (txn.vout)
  # cnxn.sendrawtransaction(txn)  # u'transaction already in block chain'  code: -27
  #pdb.set_trace()

def generate(amt=1,cnxn=None):
  if cnxn is None: cnxn = bu
  cnxn._call("generate",amt)

def spamTx(bu, numTx,addrp,amt = None,gen=False, mempoolTarget=None):
  addr = addrp
  print(">>>> Len off Address : ", len(addr))
  print ("SPAM")
  lastGenerate = -1
  # init counters
  total_interval = 0
  payments_per_sec = []
  start = time.time()
  if amt == None:
    randAmt = True
  else: randAmt = False
  for i in range(0, numTx):
    if (i!=0) and (i & 255) == 0:
      end = time.time()
      interval = end - start
      start = end
      total_interval += interval
      #print("Total interval = ", total_interval)
      current_pay_sec = 256.0/interval
      print ("issued 256 payments in %f seconds.  %f payments/sec" % (interval, current_pay_sec))
      payments_per_sec.append(current_pay_sec)
      if mempoolTarget:  # if the mempool is too big, wait for it to be reduced
        while True:
          mempoolData=bu._call("getmempoolinfo")
          mempoolBytes = mempoolData["bytes"]
          if mempoolBytes < mempoolTarget:
            break
          blockNum = bu._call("getblockcount")
          print("mempool is %d bytes, %d tx. block %d.  Waiting..." % (mempoolBytes, mempoolData["size"], blockNum))
          time.sleep(15)
    if addrp is None:
      print ("creating new address")
      addr = bu._call('getnewaddress')
    if type(addrp) is types.ListType:
      addr = addrp[i%len(addrp)]
    if randAmt:
      amt = random.randint(100*uBTC, BTC/2)
    #print ("Count ", i, "Send %d to %s" % (amt, str(addr)))
    if total_interval > BLK_GENERATION_INTERVAL:
        print("\nPayment per second:")
        print("Min : ", min(payments_per_sec))
        print("Average : ", sum(payments_per_sec)/len(payments_per_sec))
        print("Max : \n", max(payments_per_sec))
        print("Total Txns in a block in 10 mins) : \n", sum(payments_per_sec))
        del payments_per_sec[:]
        total_interval = 0
    try:
        if amt == 1234567:
            bu.sendtoaddress(addr,amt)
        else:
            send_to_address(bu, addr, amt)
    except rpc.JSONRPCError as e:
      if "Fee is larger" in str(e) and randAmt:
        pass
      else: raise
    except rpc.JSONRPCError as e:
      if gen and i > lastGenerate:  # Out of TxOuts in the wallet so commit these txn
        generate()
        print ("\nGenerated at count %d.  Interval %d" % (i, i-lastGenerate))
        lastGenerate = i
      else:
        print ("\n%d: Exception %s" % (i,str(e)))
        raise
    finally:
      #print
      pass

@timeit
def send_to_address(bu, addr, amt):
    bu.sendtoaddress(addr,amt)

def split(frm, toAddrs, cnxn, txfee=DEFAULT_TX_FEE):
  inp = []
  getcontext().prec = 8
  amount = Decimal(0)
  for tx in frm:
#      inp.append({"txid":str(tx["txid"]),"vout":tx["vout"]})
      inp.append({"txid":bitcoin.core.b2lx(tx["outpoint"].hash),"vout":tx["outpoint"].n})
      amount += tx["amount"]

  outp = {} # = { str(toAddr): str((amount-txfee)/BTC) }
  getcontext().prec = 8
  amtPer = (Decimal(amount-txfee)/len(toAddrs)).to_integral_value()
  print ("amount: ", amount, " amount per: ", amtPer, "from :", len(frm), "to: ", len(toAddrs), "tx fee: ", txfee)

  for a in toAddrs[0:-1]:
    if PerfectFractions:
      outp[str(a)] = str(amtPer/BTC)
    else:
      outp[str(a)] = float(amtPer/BTC)

  a = toAddrs[-1]
  amtPer = (amount - ((len(toAddrs)-1)*amtPer)) - txfee
  print ("final amt: ", amtPer)
  if PerfectFractions:
      outp[str(a)] = str(amtPer/BTC)
  else:
      outp[str(a)] = float(amtPer/BTC)

  try:
    txn = cnxn._call("createrawtransaction",inp, outp)
    signedtxn = cnxn._call("signrawtransaction",str(txn))
    if signedtxn["complete"]:
      cnxn._call("sendrawtransaction", signedtxn["hex"])
  except rpc.JSONRPCError as e:
    print (str(e))


def consolidate(frm, toAddr, cnxn, txfee=DEFAULT_TX_FEE):
  #out = bitcoin.core.CTxOut(frm["amount"],toAddr)
  #script = bitcoin.core.CScript()
  # bitcoin.wallet.CBitcoinAddress(toAddr)
  # pdb.set_trace()
  inp = []
  amount = Decimal(0)
  print(" frm[0] = ", frm[0])
  for tx in frm:
      # pdb.set_trace()
      if tx["spendable"] is True and tx["confirmations"] > 0:
        inp.append({"txid":bitcoin.core.b2lx(tx["outpoint"].hash),"vout":tx["outpoint"].n})
        amount += tx["amount"]

  #out = bitcoin.core.CMutableTxOut(frm["amount"],toAddr.to_scriptPubKey())
  if PerfectFractions:
     outamt = str((amount-txfee)/BTC)
  else:
     outamt = float((amount-txfee)/BTC)

  out = { str(toAddr): outamt }
  #txn = bitcoin.core.CMutableTransaction(inp,[out])
  txn = cnxn._call("createrawtransaction",inp, out)
  signedtxn = cnxn._call("signrawtransaction",str(txn))
  if signedtxn["complete"]:
    cnxn._call("sendrawtransaction", signedtxn["hex"])

def consolidate2(frm, toAddr, cnxn):
  inp = []
  for tx in frm["txids"]:
    txinfo = cnxn.gettransaction(tx)
    print (txinfo)
    vout = None
    for d in txinfo["details"]:
      if d["address"] == frm["address"]:
        vout = d["vout"]
        break
    if not vout is None:
      inp.append({"txid":str(tx),"vout":vout})

  pdb.set_trace()

  #out = bitcoin.core.CMutableTxOut(frm["amount"],toAddr.to_scriptPubKey())
  out = { str(toAddr): str(frm["amount"]) }
  #txn = bitcoin.core.CMutableTransaction(inp,[out])
  txn = cnxn._call("createrawtransaction",inp, out)
  signedtxn = cnxn._call("signrawtransaction",str(txn))
  cnxn.sendrawtransaction(signedtxn)


def consolidate2(frm, toAddr, cnxn):
  pdb.set_trace()

  inp = []
  for tx in frm["txids"]:
    txinfo = cnxn.gettransaction(tx)
    print (txinfo)
    vout = None
    for d in txinfo["details"]:
      if d["address"] == frm["address"]:
        vout = d["vout"]
        break
    if not vout is None:
      inp.append(bitcoin.core.CMutableTxIn(bitcoin.core.COutPoint(tx, vout)))


  out = bitcoin.core.CMutableTxOut(frm["amount"],toAddr.to_scriptPubKey())
  txn = bitcoin.core.CMutableTransaction(inp,[out])
  cnxn.sendrawtransaction(txn)

if __name__ == "__main__":
  idx = 1
  if len(sys.argv) > 1:
    if sys.argv[1] == "help":
      print("./txnTest.py <network> <operation> [operation specific arguments]")
      print('  network can be: "testnet", "regtest", "nol", "main"')
      print('  operation can be: "split", "join", "spam", "unspent", "info"')
      print("    split: create more UTXOs.")
      print("      parameters: [nSplits: takes every UTXO that has sufficient balance and splits it into this many more UTXOs, default 25]")
      print("      example: ./txnTest.py nol split 10")
      print("    join: consolidate UTXOs.")
      print("      parameters: <nJoin: take this many UTXOs and join them into 1>  <nRepeat: repeat the join this many times>")
      print("      example that joins 50 UTXOs into one output 2 times: ./txnTest.py nol join 50 2")
      print("    spam: generate a lot of transactions, by paying to myself.")
      print("      example: ./txnTest.py nol spam")
      print(" ")
      print(" User can input localhost at the end of the command lines to indicate bitcoind is runnning on the same machine")
      print(" Without localhost, it will send commands to remote host with HOST_IP and HOST_PORT defined")
      print(" User can also specify host ip and port with ipaddress=10.xx.xx.xxx:yyyyy format")
      print("      example 1:  ./txnTest.py regtest unspent localhost")
      print("                  This wallet has 22372 unspent outputs.")
      print("      example 2:  ./txnTest.py regtest unspent")
      print("                  hostname =  10.54.150.74")
      print("                  This wallet has 411 unspent outputs.")
      print("      example 3:  ./txnTest.py regtest unspent ipaddress=10.54.150.74:19011")
      print("                  hostname =  10.54.150.74")
      print("                  This wallet has 411 unspent outputs.")
      sys.exit(1)
    if sys.argv[idx] == "testnet":
      bitcoin.SelectParams('testnet')
      idx+=1
    elif sys.argv[idx] == "regtest":
      bitcoin.SelectParams('regtest')
      idx+=1
    elif sys.argv[idx] == "nol":
      bitcoin.SelectParams('nol')
      idx+=1
    elif sys.argv[idx] == "main":
      bitcoin.SelectParams('mainnet')
      idx+=1
    else:
      print("Invalid network %s" % sys.argv[idx])
      sys.exit(-1)

  if len(sys.argv) > idx:
    op = sys.argv[idx]
  else: op = "info"
  main(op, sys.argv[idx+1:])

def Test():
  if 1:
      bitcoin.SelectParams('mainnet')
      bitcoin.params.DEFAULT_PORT = 9333
      bitcoin.params.RPC_PORT = 9332
      bitcoin.params.DNS_SEEDS = tuple()
  main("join",["100","100"])

