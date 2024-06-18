import datetime
from web3.types import BlockData, HexBytes

from celery import shared_task, group
from celery.contrib import rdb

from .models import ConfigMonitorBlock, Block, Transaction, ConfigNode
from lib.services.processor import sync_process_block_evm, web3_build
from lib.services.types import SerializedWeb3
from django.db import transaction as db_transaction

@shared_task
def process_transaction(sweb3: SerializedWeb3, tx_hash: HexBytes):
    # Not sure is it good. Create many sockets, it would be better create shared socket or pool
    web3 = web3_build(sweb3['kind'], sweb3['url'])
    transaction = web3.eth.get_transaction(tx_hash)
    return transaction  

@shared_task
def process_transactions(blockchain_id:int, sweb3: SerializedWeb3, block: BlockData):
    blockchain = ConfigNode.objects.get(id=blockchain_id)
    if blockchain is None:
        return
    return
    # convert timestamp to string
    with db_transaction.atomic():
        tm = datetime.datetime.fromtimestamp(block['timestamp'])
        block_db = Block.objects.create(
            number=block['number'],
            tx=block['hash'],
            parent_tx=block['parentHash'],
            nonce=block['nonce'],
            sha3_uncles=block['sha3Uncles'],
            logs_bloom=block['logsBloom'],
            state_root=block['stateRoot'],
            receipts_root=block['receiptsRoot'],
            miner=block['miner'],
            difficulty=block['difficulty'],
            total_difficulty=block['totalDifficulty'],
            extra_data=block['extraData'],
            size=block['size'],
            gas_limit=block['gasLimit'],
            gas_used=block['gasUsed'],
            time=tm,
            reward=0, # TODO see WithdrawalData TransactionFee + Burnt Fee
            fee=0, # TODO see WithdrawalData
            blockchain=blockchain,
            transactions=len(block['transactions']),
            uncles=len(block['uncles'])
        )
        transactions_db = []
        transactions = group(process_transaction.s(sweb3, tx_hash) for tx_hash in block['transactions']).apply_async()

        # wait for all transactions to be processed
        for async_result in transactions:
            transaction = async_result.get()
            if transaction.failed():                
                process_transaction.retry(countdown=10)
            transactions_db.append(Transaction(
                hash=transaction['hash'],
                nonce=transaction['nonce'],
                block_hash=transaction['blockHash'],
                block_number=transaction['blockNumber'],
                transaction_index=transaction['transactionIndex'],
                from_address=transaction['from'],
                to_address=transaction['to'],
                value=transaction['value'],
                gas=transaction['gas'],
                gas_price=transaction['gasPrice'],
                input=transaction['input'],
                block=block_db
            ))
        Transaction.objects.bulk_create(transactions_db)
    
    assert block['transactions'] == len(transactions_db)

@shared_task
def process_sync_blocks(config_id: int): 
    try:
        monitor = ConfigMonitorBlock.objects.get(id=config_id)
        if monitor.enabled:
            web3 = monitor.node.get_web3()
            last_block = monitor.objects.last_block()
            start = web3.eth.block_number
            if last_block:
                start = last_block.number
            
        for block in sync_process_block_evm(web3.eth, start):
            process_transactions.delay(monitor.node.id, web3.eth, block)

    except ConfigMonitorBlock.DoesNotExist:
        return