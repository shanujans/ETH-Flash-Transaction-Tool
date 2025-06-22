# ETH Flash Transaction Tool

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A lightweight CLI tool for sending Ethereum transactions quickly and securely. Supports both mainnet and testnet operations with mock mode for safe testing.

## Features

- 🚀 Send ETH transactions with a single command
- 💰 Check wallet balances instantly
- 🔐 Secure wallet management
- 🧪 Mock mode for safe testing
- 🌐 Automatic connection to reliable RPC providers
- 📦 Simple state management with JSON storage

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

```bash
# Clone the repository
git clone https://github.com/yourusername/flash-transaction-tool.git
cd flash-transaction-tool

# Create virtual environment
python -m venv venv

# Activate environment
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage
Add a Wallet
```bash
python flash_tx.py add-wallet --name my_wallet --key YOUR_PRIVATE_KEY
```
Check Balance
```bash
python flash_tx.py balance --wallet my_wallet
```
Send ETH
```bash
python flash_tx.py send --from my_wallet --to 0xRecipientAddress --amount 0.1
```
Mock Mode (Safe Testing)
```bash
python flash_tx.py --mock send --from test_wallet --to 0xTestAddress --amount 1.0
```

### Configuration
Networks
The tool supports:

sepolia (default testnet)

mainnet

To switch networks, modify the ETHChain class in flash_tx.py.

### Environment Variables
Create .env File following Tect
```TRUST_WALLET_PRIVATE_KEY=your_private_key```

### Getting Test ETH
For Sepolia testnet:

1. [Alchemy Faucet](https://sepoliafaucet.com/)

2. [Infura Faucet](https://www.infura.io/faucet/sepolia)

3. [PoW Faucet](https://sepolia-faucet.pk910.de/)


### Security Notes
🔒 Wallet data is stored in wallet_state.json (keep this file secure!)

🚫 Never commit wallet files to version control

💡 Use mock mode for development and testing

⚠️ Mainnet transactions use real funds - double-check before sending

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**  
   [Fork this repository](https://github.com/shanujans/ETH-Flash-Transaction-Tool/fork) to your GitHub account

2. **Set up your development environment**  
   ```bash
   git clone https://github.com/shanujans/ETH-Flash-Transaction-Tool.git
   cd flash-transaction-tool

### License
Distributed under the MIT License. See LICENSE for more information.

### Disclaimer
This tool is for educational purposes only. Use at your own risk. The developers are not responsible for any loss of funds.
