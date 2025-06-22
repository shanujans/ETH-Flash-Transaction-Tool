import os
import json
import re
import click
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount

# ---------------------- Blockchain Connection ----------------------
class ETHChain:
    NETWORKS = {
        "mainnet": [
            "https://cloudflare-eth.com",
            "https://rpc.ankr.com/eth",
            "https://eth.public-rpc.com"
        ],
        "sepolia": [
            "https://rpc.sepolia.org",
            "https://sepolia.drpc.org",
            "https://rpc.notadegen.com/sepolia"
        ]
    }

    def __init__(self, network="sepolia"):
        self.network = network
        self.w3 = None
        self._connect()

    def _connect(self):
        for rpc_url in self.NETWORKS.get(self.network, []):
            try:
                self.w3 = Web3(Web3.HTTPProvider(rpc_url))
                if self.w3.is_connected() and self.w3.eth.chain_id > 0:
                    print(f"✅ Connected to {self.network} via {rpc_url}")
                    return
            except:
                continue
        raise ConnectionError(f"Could not connect to any {self.network} endpoint")

    def create_tx(self, from_addr, to_addr, amount):
        return {
            'from': from_addr,
            'to': to_addr,
            'value': self.w3.to_wei(amount, 'ether'),
            'gas': 21000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(from_addr),
            'chainId': self.w3.eth.chain_id
        }

    def send_transaction(self, signed_tx):
        return self.w3.eth.send_raw_transaction(signed_tx).hex()

    def get_balance(self, address):
        balance_wei = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance_wei, 'ether')

# ---------------------- Mock Blockchain ----------------------
class MockChain:
    def __init__(self):
        self.network = "mock"
        
    def create_tx(self, from_addr, to_addr, amount):
        return {'mock': True, 'value': amount}
    
    def send_transaction(self, signed_tx):
        return "0xmocked_tx_hash"
    
    def get_balance(self, address):
        return 10.0  # Mock balance

# ---------------------- Wallet Management ----------------------
class Wallet:
    def __init__(self):
        self.account = None

    def get_address(self, asset):
        if not self.account:
            raise ValueError("Wallet not initialized")
        return self.account.address

    def sign_transaction(self, tx_data):
        if not self.account:
            raise ValueError("Wallet not initialized")
        return self.account.sign_transaction(tx_data).rawTransaction

    def initialize(self, private_key):
        """Initialize wallet with a private key"""
        key = private_key.strip()
        
        # Remove 0x prefix if present
        if key.startswith('0x'):
            key = key[2:]
            
        # Validate key is 64 hex characters
        if not re.match(r'^[0-9a-fA-F]{64}$', key):
            raise ValueError("Invalid private key format - must be 64 hex characters (with or without 0x prefix)")
            
        self.account = Account.from_key(key)

# ---------------------- Core Engine ----------------------
class FlashEngine:
    STATE_FILE = "wallet_state.json"
    
    def __init__(self, mock=False):
        self.wallets = {}
        self.mock = mock
        self.chain = MockChain() if mock else ETHChain()
        self.load_state()

    def add_wallet(self, name, private_key):
        """Add or update a wallet"""
        try:
            wallet = Wallet()
            wallet.initialize(private_key)
            
            # Store the validated key (without 0x prefix)
            key = private_key.strip()
            if key.startswith('0x'):
                key = key[2:]
            self.wallets[name] = {"private_key": key}
            self.save_state()
            return True
        except Exception as e:
            raise ValueError(f"Failed to add wallet: {str(e)}")

    def get_wallet(self, name):
        if name not in self.wallets:
            raise ValueError(f"Wallet '{name}' not found")
            
        wallet = Wallet()
        wallet.initialize(self.wallets[name]["private_key"])
        return wallet

    def execute_tx(self, from_wallet, to_address, amount):
        wallet = self.get_wallet(from_wallet)
        from_address = wallet.get_address("ETH")
        tx_data = self.chain.create_tx(from_address, to_address, amount)
        signed_tx = wallet.sign_transaction(tx_data)
        return self.chain.send_transaction(signed_tx)

    def get_balance(self, wallet_name):
        wallet = self.get_wallet(wallet_name)
        address = wallet.get_address("ETH")
        return self.chain.get_balance(address)

    def save_state(self):
        with open(self.STATE_FILE, 'w') as f:
            json.dump({"wallets": self.wallets}, f)

    def load_state(self):
        if os.path.exists(self.STATE_FILE):
            with open(self.STATE_FILE, 'r') as f:
                self.wallets = json.load(f).get("wallets", {})

# ---------------------- CLI Interface ----------------------
@click.group()
@click.option('--mock', is_flag=True, help='Use mock mode')
@click.pass_context
def cli(ctx, mock):
    """Flash Transaction Tool"""
    ctx.obj = {'MOCK': mock}
    if mock:
        click.secho("⚠️ MOCK MODE - NO REAL TRANSACTIONS", fg='yellow')

@cli.command(name='add-wallet')
@click.option('--name', required=True, help='Wallet name')
@click.option('--key', required=True, help='Private key (64 hex chars, with or without 0x prefix)')
@click.pass_context
def add_wallet(ctx, name, key):
    """Add a new wallet"""
    try:
        engine = FlashEngine(mock=ctx.obj['MOCK'])
        if engine.add_wallet(name, key):
            click.echo(f"✅ Wallet '{name}' added successfully")
            click.echo(f"Address: {engine.get_wallet(name).get_address('ETH')}")
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red')

@cli.command(name='send')
@click.option('--from', 'from_wallet', required=True, help='Sending wallet')
@click.option('--to', required=True, help='Receiving address')
@click.option('--amount', type=float, required=True, help='Amount in ETH')
@click.pass_context
def send(ctx, from_wallet, to, amount):
    """Send ETH"""
    try:
        engine = FlashEngine(mock=ctx.obj['MOCK'])
        tx_hash = engine.execute_tx(from_wallet, to, amount)
        click.echo(f"\n⚡ Transaction Sent")
        click.echo(f"From: {engine.get_wallet(from_wallet).get_address('ETH')}")
        click.echo(f"To: {to}")
        click.echo(f"Amount: {amount} ETH")
        click.echo(f"TX Hash: {tx_hash}")
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red')

@cli.command(name='balance')
@click.option('--wallet', required=True, help='Wallet name')
@click.pass_context
def balance(ctx, wallet):
    """Check balance"""
    try:
        engine = FlashEngine(mock=ctx.obj['MOCK'])
        balance = engine.get_balance(wallet)
        address = engine.get_wallet(wallet).get_address("ETH")
        click.echo(f"\n💰 Balance for {address}: {balance} ETH")
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red')

if __name__ == '__main__':
    cli()
