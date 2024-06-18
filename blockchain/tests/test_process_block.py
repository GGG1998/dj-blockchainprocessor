from django.test import TestCase
from unittest.mock import patch

from web3 import Web3, EthereumTesterProvider
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from blockchain.tasks import process_transaction, process_transactions
from blockchain.models import Block, Transaction, ConfigNode, ConfigMonitorBlock

from pytest_celery.api.setup import CeleryTestSetup

import pytest

class TestProcessBlocks(TestCase):
    def setUp(self):
        # SETUP ETHEREUM TESTER
        self.evm = EthereumTesterProvider()
        self.accounts = self.evm.ethereum_tester.get_accounts()
        l = self.evm.ethereum_tester.send_transaction({
            'from': self.accounts[0],
            'to': self.accounts[1],
            'value': 1,
            'gas': 21000,
        })
        # print(l)
        # self.evm.ethereum_tester.mine_block()

        # SETUP DJANGO DB
        interval = IntervalSchedule.objects.create(
            every=1,
            period=IntervalSchedule.HOURS,
        )
        periodic_task = PeriodicTask.objects.create(
            name="test",
            task="blockchain.tasks.process_transactions",
            enabled=False,
            interval=interval,
        )
        self.blockchain = ConfigNode.objects.create(
            name="test",
            url="http://localhost:8545",
            chain_id=1,
            network_id=1,
            symbol="ETH",
        )
        self.monitor = ConfigMonitorBlock.objects.create(
            node=self.blockchain,
            enabled=True,
            task=periodic_task,
        )

    @patch('blockchain.tasks.process_transaction.delay')
    def test_process_transaction_success(self, process_transaction_delay):
        process_transaction.delay(None, "0x1234567890")
        process_transaction_delay.assert_called_once()
    
    # @pytest.mark.celery(result_backend='rpc')
    def test_process_transactions(self):
        # assert celery_setup.ready()

        w = Web3(self.evm)
        block = w.eth.get_block('latest')
        
        self.assertEqual(len(block['transactions']), 1, "Block should have 1 transaction")

        process_transactions(self.blockchain.id, {
            'kind': 'http',
            'url': 'http://localhost:8545',
        }, block)

        # check database
        self.assertEqual(Block.objects.count(), 1)
        self.assertEqual(Transaction.objects.count(), 1)

        
        