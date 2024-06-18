import pytest
from web3 import Web3
from web3.providers.eth_tester.main import (
    EthereumTesterProvider,
) 

from lib.services.processor import sync_process_block_evm, sync_transaction_evm

@pytest.fixture
def backend():
    return EthereumTesterProvider()

@pytest.fixture
def provider(backend):
    w3 = Web3(backend)
    return w3.eth

def test_sync_process_block_evm(provider, backend):
    start, end = 5, 10
    backend.ethereum_tester.mine_blocks(end)
    for block in sync_process_block_evm(provider, start):
        assert 'number' in block
        assert block['number'] >= start

    head = provider.get_block_number()
    assert head == end

def test_sync_transaction_evm(provider):
    start = 0
    for block in sync_process_block_evm(provider, start):
        for tx in sync_transaction_evm(provider, block):
            assert 'hash' in tx