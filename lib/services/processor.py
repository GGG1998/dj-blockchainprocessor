from web3 import Web3, HTTPProvider, WebsocketProvider
from web3.eth import Eth
from web3.types import BlockData, TxReceipt
from typing import Iterator

from lib.services.types import KIND

def web3_build(kind: str, url: str) -> Web3:
    if KIND.get(kind) is None:
        raise Exception('Invalid kind')
    if kind == 'http':
        return Web3(HTTPProvider(url))
    return Web3(WebsocketProvider(url))


def sync_process_block_evm(provider: Eth, start:int) -> Iterator[BlockData]:
    head = provider.get_block_number()
    for block_number in range(start, head):
        block = provider.get_block(block_number)
        if block:
            yield block

def sync_transaction_evm(provider: Eth, block: BlockData) -> Iterator[TxReceipt]:
    for tx_hash in block['transactions']:
        tx = provider.get_transaction(tx_hash)
        if tx:
            yield tx
