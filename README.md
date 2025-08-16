# Bitcoin Legacy Wallet Scanner

High-performance scanner for generating and checking balances of Bitcoin legacy wallets (P2PKH, addresses starting with "1") using a local bitcoin-core node.

## ⚠️ IMPORTANT SECURITY WARNING

**THIS TOOL GENERATES PRIVATE KEYS!**

- **DO NOT USE** for real wallets with money
- **DO NOT USE** for theft or hacking
- **ONLY** for educational purposes and testing
- Private keys are saved in CSV files - protect them accordingly
- Author is not responsible for misuse

## 🚀 Features

- **High Performance**: ~100,000 addresses/min generation, ~50,000 checks/min
- **Legacy P2PKH**: Generation of addresses starting with "1"
- **Batch Checking**: Using `scantxoutset` for efficient balance checking
- **TUI Interface**: Intuitive terminal control
- **Multiprocessing**: Automatic CPU core detection
- **Fault Tolerance**: Retries, exponential backoff
- **State Persistence**: Ability to resume work
- **File Rotation**: Automatic output file size management

## 📋 Requirements

- **Python 3.10+**
- **Ubuntu/Debian** (or other Linux distribution)
- **Bitcoin Core** full node with accessible `bitcoin-cli`
- **Minimum 4GB RAM** (8GB+ recommended)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd bitcoin-keygen
```

### 2. Install dependencies

```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 3. Install Bitcoin Core

```bash
# Add Bitcoin Core PPA
sudo add-apt-repository ppa:bitcoin/bitcoin
sudo apt update
sudo apt install bitcoind bitcoin-cli

# Or compile from source (for latest version)
# https://github.com/bitcoin/bitcoin/blob/master/doc/build-unix.md
```

### 4. Configure Bitcoin Core

```bash
# Create configuration file
mkdir ~/.bitcoin
cat > ~/.bitcoin/bitcoin.conf << EOF
# Basic settings
daemon=1
server=1
rpcuser=your_username
rpcpassword=your_secure_password
rpcallowip=127.0.0.1

# For scanner functionality
txindex=1
blockfilterindex=1

# Network (choose one)
# mainnet (default)
# testnet=1
# regtest=1
EOF

# Start bitcoind
bitcoind

# Check synchronization
bitcoin-cli getblockchaininfo
```

## ⚙️ Configuration

Edit `config.yaml` according to your needs:

```yaml
# Batch size for RPC calls
batch_size: 512

# Number of workers (auto = automatic detection)
gen_workers: auto
rpc_workers: auto

# Path to bitcoin-cli
bitcoin_cli_path: "bitcoin-cli"

# Output directory
output_dir: "./out"
```

## 🎯 Usage

### Basic commands

```bash
# Start with TUI interface
python3 btc_legacy_scanner.py

# Start in headless mode
python3 btc_legacy_scanner.py --headless --start

# Run for specified time
python3 btc_legacy_scanner.py --headless --start --duration 3600

# Use custom configuration
python3 btc_legacy_scanner.py --config my_config.yaml
```

### TUI Controls

In TUI mode use keys:
- **s** - Start/Resume
- **p** - Pause
- **q** - Quit

### CLI Options

```bash
python3 btc_legacy_scanner.py --help

Options:
  --config CONFIG        Configuration file path
  --start               Start scanning immediately
  --pause               Pause scanning
  --resume              Resume scanning
  --headless            Run without TUI interface
  --duration SECONDS    Run for specified seconds then stop
  --dry-run             Generate keys but mock balance checks
  --output-dir DIR      Output directory
  --batch-size SIZE     Batch size for RPC calls
  --gen-workers N       Number of generation workers
  --rpc-workers N       Number of RPC workers
```

## 📊 Output Files

### 1. `btc_adress_w_balance.csv`
Addresses with positive balance:
```
<public_address>;<private_key_wif>;<balance_sats>
1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa;5KJvsngHeMpm884wtkgcTvQvq9d2Prnju6yJpAGpLt1xL2kQn9j;100000000
```

### 2. `bad_adress`
Addresses with zero balance (one per line):
```
1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2
1C1avBMqJKLQj4nXqrNkBL5MfmvSBG8u8x
```

### 3. `scanner.log`
Scanner operation log with INFO/WARN/ERROR levels

### 4. `state.json`
Scanner state for resuming work

## 🔧 Performance Optimization

### 1. Batch size configuration

```yaml
# Increase for better RPC performance
batch_size: 1024

# But not too much - may cause timeouts
batch_size: 2048
```

### 2. Number of workers

```yaml
# For key generation (CPU-bound)
gen_workers: 8  # or number of CPU cores

# For RPC calls (I/O-bound)
rpc_workers: 8  # depends on network bandwidth
```

### 3. Queue size

```yaml
# Increase if you have a lot of RAM
queue_max: 500000
```

## 🚨 Troubleshooting

### "bitcoin-cli not found" error
```bash
# Check path
which bitcoin-cli

# Add to PATH
export PATH=$PATH:/usr/local/bin
```

### "Connection refused" error
```bash
# Check bitcoind status
bitcoin-cli getblockchaininfo

# Check RPC configuration
cat ~/.bitcoin/bitcoin.conf
```

### Low performance
```bash
# Check CPU usage
htop

# Check logs
tail -f scanner.log

# Increase number of workers
--gen-workers 16 --rpc-workers 8
```

### Memory issues
```bash
# Reduce queue size
queue_max: 50000

# Reduce batch size
batch_size: 256
```

## 📈 Performance Monitoring

### TUI Metrics
- Generation rate (addresses/min)
- Check rate (addresses/min)
- Queue sizes
- Found with balance count

### Logging
```bash
# View logs in real time
tail -f scanner.log

# Filter by level
grep "ERROR" scanner.log
grep "WARN" scanner.log
```

## 🔒 Security

### Recommendations
1. **Use virtual environment**
2. **Don't run as root**
3. **Restrict access to output files**
4. **Regularly rotate logs**
5. **Monitor resource usage**

### File access restrictions
```bash
# Create protected directory
mkdir -p ~/bitcoin-scanner/out
chmod 700 ~/bitcoin-scanner/out

# Run with restricted permissions
python3 btc_legacy_scanner.py --output-dir ~/bitcoin-scanner/out
```

## 🤝 Contributing

### Bug reports
1. Check existing issues
2. Specify Python and OS versions
3. Attach logs and configuration
4. Describe reproduction steps

### Feature suggestions
1. Describe problem/idea
2. Propose solution
3. Discuss with community

## 📄 License

This project is provided "as is" for educational purposes. Use at your own risk.

## ⚡ Performance

### Test results (Intel i7-8700K, 32GB RAM)
- **Generation**: ~150,000 addresses/min
- **Checking**: ~75,000 addresses/min
- **Memory**: ~2-4GB under full load
- **CPU**: 80-90% during generation, 20-30% during checking

### Optimize for your system
```bash
# Performance benchmark
python3 btc_legacy_scanner.py --dry-run --duration 300

# Resource usage analysis
python3 btc_legacy_scanner.py --headless --start --duration 600
```

## 🔗 Useful Links

- [Bitcoin Core Documentation](https://bitcoin.org/en/developer-documentation)
- [secp256k1 Library](https://github.com/bitcoin-core/secp256k1)
- [Base58Check Encoding](https://en.bitcoin.it/wiki/Base58Check_encoding)
- [Bitcoin Address Types](https://en.bitcoin.it/wiki/Address)

---

**Remember**: This tool is intended only for educational purposes and testing. Do not use for real wallets!
