from django.db import models
from django_celery_beat.models import PeriodicTask
from web3 import Web3, AsyncWeb3


class Rule(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name
    
class ConfigNode(models.Model):
    PROTOCOL = (
        ('http', 'HTTP'),
        ('ws', 'WebSocket'),
    )

    id = models.AutoField(primary_key=True)
    kind = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    chain_id = models.IntegerField()
    url = models.URLField()
    network = models.CharField(max_length=255)
    network_id = models.IntegerField()
    api_key = models.CharField(max_length=255)
    protocol = models.CharField(max_length=10, choices=PROTOCOL, default='http')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_web3(self) -> Web3:
        if self.protocol == 'http':
            return Web3(Web3.HTTPProvider(self.url))
        elif self.protocol == 'ws':
            return Web3(Web3.WebsocketProvider(self.url))
        else:
            raise Exception('Invalid protocol')
        
    def is_connected(self) -> bool:
        try:
            web3 = self.get_web3()
            return web3.is_connected()
        except Exception:
            return False

    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ('kind', 'name')
        verbose_name = 'Node'
        verbose_name_plural = 'Nodes'

class ConfigMonitorBlock(models.Model):
    id = models.AutoField(primary_key=True)
    node = models.ForeignKey(ConfigNode, on_delete=models.CASCADE)
    task = models.ForeignKey(PeriodicTask, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    rules = models.ManyToManyField(Rule)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Monitor Block'
        verbose_name_plural = 'Monitor Blocks'


class BlockManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related('blockchain')
    
    def get_last_block(self, _id:int) -> 'Block':
        return self.get_queryset().filter(blockchain__id=_id).order_by('-number').first()
        

class Block(models.Model):
    id = models.AutoField(primary_key=True)
    tx = models.CharField(max_length=255)
    parent_tx = models.CharField(max_length=255)
    receipts_root = models.CharField(max_length=255)
    state_root = models.CharField(max_length=255)
    number = models.IntegerField()
    time = models.DateTimeField()
    size = models.IntegerField()
    difficulty = models.DecimalField(max_digits=20, decimal_places=10)
    miner = models.CharField(max_length=255)
    reward = models.DecimalField(max_digits=20, decimal_places=10)
    fee = models.DecimalField(max_digits=20, decimal_places=10)
    extra_data = models.TextField()
    gas_limit = models.IntegerField()
    gas_used = models.IntegerField()
    nonce = models.CharField(max_length=255)
    sha3_uncles = models.CharField(max_length=255)
    total_difficulty = models.DecimalField(max_digits=20, decimal_places=10)
    transactions = models.IntegerField()
    uncles = models.IntegerField()
    logs_bloom = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    blockchain = models.ForeignKey(ConfigNode, on_delete=models.PROTECT, default=None)

    objects = models.Manager()
    blockmanager = BlockManager()

    def __str__(self):
        return self.tx
    
    class Meta:
        ordering = ['-number']
        verbose_name = 'Block'
        verbose_name_plural = 'Blocks'
    
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    tx = models.CharField(max_length=255)
    block = models.ForeignKey(Block, on_delete=models.PROTECT, default=None)
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=20, decimal_places=10)
    gas = models.IntegerField()
    gas_price = models.DecimalField(max_digits=20, decimal_places=10)
    input = models.TextField()
    nonce = models.IntegerField()
    transaction_index = models.IntegerField()
    v = models.CharField(max_length=255)
    r = models.CharField(max_length=255)
    s = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hash
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'