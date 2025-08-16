#!/usr/bin/env python3
"""
Bitcoin Legacy Wallet Scanner
High-performance scanner for P2PKH addresses with balance checking via bitcoin-cli
"""

import os
import sys
import time
import json
import hashlib
import hmac
import base64
import asyncio
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Generator, Tuple
from pathlib import Path
import argparse
import logging
import signal
from queue import Queue, Empty
import threading
from datetime import datetime
import yaml
import blessed
from blessed import Terminal

# Try to import coincurve, fallback to ecdsa
try:
    import coincurve
    HAS_COINCURVE = True
except ImportError:
    HAS_COINCURVE = False
    try:
        import ecdsa
        HAS_ECDSA = True
    except ImportError:
        HAS_ECDSA = False
        print("ERROR: Neither coincurve nor ecdsa available. Install one of them.")
        sys.exit(1)

# Constants
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
VERSION_BYTE = 0x00  # Mainnet P2PKH
COMPRESSED_FLAG = 0x01

@dataclass
class WalletInfo:
    """Wallet information container"""
    address: str
    private_key_wif: str
    balance_sats: int = 0

@dataclass
class ScannerState:
    """Scanner state for persistence"""
    last_generated: int = 0
    last_checked: int = 0
    found_with_balance: int = 0
    start_time: float = 0.0
    is_running: bool = False
    is_paused: bool = False

class Base58Check:
    """Base58Check encoding/decoding optimized for Bitcoin addresses"""
    
    ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    BASE = len(ALPHABET)
    
    @staticmethod
    def encode(data: bytes) -> str:
        """Encode bytes to Base58Check"""
        # Add version byte and double SHA256 for checksum
        versioned = bytes([VERSION_BYTE]) + data
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        full_data = versioned + checksum
        
        # Convert to base58
        n = int.from_bytes(full_data, 'big')
        res = []
        while n > 0:
            n, r = divmod(n, Base58Check.BASE)
            res.append(Base58Check.ALPHABET[r])
        
        # Handle leading zeros
        for byte in full_data:
            if byte == 0:
                res.append(Base58Check.ALPHABET[0])
            else:
                break
        
        return ''.join(reversed(res))

class KeyGenerator:
    """High-performance Bitcoin private key generator"""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self._pool = None
        
    def _generate_private_key(self) -> int:
        """Generate secure random private key in secp256k1 range"""
        while True:
            # Generate 32 random bytes
            key_bytes = os.urandom(32)
            key_int = int.from_bytes(key_bytes, 'big')
            
            # Ensure it's in valid range
            if 0 < key_int < SECP256K1_N:
                return key_int
    
    def _private_to_public(self, private_key: int) -> bytes:
        """Convert private key to compressed public key"""
        if HAS_COINCURVE:
            # Use coincurve for better performance
            private_key_bytes = private_key.to_bytes(32, 'big')
            public_key = coincurve.PublicKey.from_secret(private_key_bytes)
            return public_key.format(compressed=True)
        else:
            # Fallback to ecdsa
            signing_key = ecdsa.SigningKey.from_secret_exponent(private_key, curve=ecdsa.SECP256k1)
            verifying_key = signing_key.get_verifying_key()
            public_key_bytes = verifying_key.to_string()
            
            # Compress public key
            x = public_key_bytes[:32]
            y = public_key_bytes[32:]
            if int.from_bytes(y, 'big') % 2 == 0:
                return bytes([0x02]) + x
            else:
                return bytes([0x03]) + x
    
    def _public_to_address(self, public_key: bytes) -> str:
        """Convert public key to P2PKH address"""
        # SHA256 + RIPEMD160
        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Base58Check encoding
        return Base58Check.encode(ripemd160_hash)
    
    def _private_to_wif(self, private_key: int, compressed: bool = True) -> str:
        """Convert private key to WIF format"""
        # Add version byte (0x80 for mainnet)
        versioned = bytes([0x80]) + private_key.to_bytes(32, 'big')
        
        if compressed:
            versioned += bytes([COMPRESSED_FLAG])
        
        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        full_data = versioned + checksum
        
        # Base58 encoding
        return base64.b64encode(full_data).decode('ascii')
    
    def generate_batch(self) -> List[WalletInfo]:
        """Generate a batch of wallet information"""
        wallets = []
        
        for _ in range(self.batch_size):
            private_key = self._generate_private_key()
            public_key = self._private_to_public(private_key)
            address = self._public_to_address(public_key)
            wif = self._private_to_wif(private_key)
            
            wallets.append(WalletInfo(
                address=address,
                private_key_wif=wif,
                balance_sats=0
            ))
        
        return wallets

class BitcoinRPCScanner:
    """Bitcoin RPC scanner using scantxoutset for batch balance checking"""
    
    def __init__(self, config: dict):
        self.config = config
        self.bitcoin_cli_path = config.get('bitcoin_cli_path', 'bitcoin-cli')
        self.network = config.get('network', 'mainnet')
        self.rpc_timeout = config.get('rpc_timeout_sec', 120)
        self.batch_size = config.get('batch_size', 512)
        self.max_retries = 3
        self.base_delay = 1.0
        
    def _build_descriptors(self, addresses: List[str]) -> List[Dict[str, str]]:
        """Build descriptors for scantxoutset"""
        return [{"desc": f"addr({addr})"} for addr in addresses]
    
    def _execute_bitcoin_cli(self, command: List[str]) -> Dict:
        """Execute bitcoin-cli command with timeout"""
        import subprocess
        
        try:
            result = subprocess.run(
                [self.bitcoin_cli_path] + command,
                capture_output=True,
                text=True,
                timeout=self.rpc_timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"bitcoin-cli error: {result.stderr}")
            
            return json.loads(result.stdout)
            
        except subprocess.TimeoutExpired:
            raise Exception("bitcoin-cli timeout")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from bitcoin-cli")
    
    def scan_addresses(self, addresses: List[str]) -> Dict[str, int]:
        """Scan addresses for balances using scantxoutset"""
        if not addresses:
            return {}
        
        # Build descriptors
        descriptors = self._build_descriptors(addresses)
        
        # Execute scantxoutset
        command = ["scantxoutset", "start", json.dumps(descriptors)]
        
        for attempt in range(self.max_retries):
            try:
                result = self._execute_bitcoin_cli(command)
                
                # Parse results
                balances = {}
                if 'utxos' in result:
                    for utxo in result['utxos']:
                        address = utxo.get('address')
                        if address in addresses:
                            balances[address] = balances.get(address, 0) + int(utxo.get('amount', 0) * 100000000)
                
                return balances
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                
                # Exponential backoff
                delay = self.base_delay * (2 ** attempt)
                time.sleep(delay)
        
        return {}

class OutputWriter:
    """Thread-safe output writer with file rotation"""
    
    def __init__(self, output_dir: str, rotate_size_mb: int = 100):
        self.output_dir = Path(output_dir)
        self.rotate_size_mb = rotate_size_mb
        self.output_dir.mkdir(exist_ok=True)
        
        self.balance_file = self.output_dir / "btc_adress_w_balance.csv"
        self.bad_address_file = self.output_dir / "bad_adress"
        
        self.lock = threading.Lock()
        self._init_files()
    
    def _init_files(self):
        """Initialize output files"""
        # Create balance file if it doesn't exist
        if not self.balance_file.exists():
            self.balance_file.touch()
        
        # Create bad address file if it doesn't exist
        if not self.bad_address_file.exists():
            self.bad_address_file.touch()
    
    def _check_rotation(self, file_path: Path):
        """Check if file needs rotation"""
        if file_path.stat().st_size > self.rotate_size_mb * 1024 * 1024:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_path = file_path.parent / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            # Rotate file
            file_path.rename(rotated_path)
            file_path.touch()
    
    def write_balance(self, wallet: WalletInfo):
        """Write wallet with balance to CSV file"""
        with self.lock:
            self._check_rotation(self.balance_file)
            
            line = f"{wallet.address};{wallet.private_key_wif};{wallet.balance_sats}\n"
            with open(self.balance_file, 'a', encoding='utf-8') as f:
                f.write(line)
    
    def write_bad_address(self, address: str):
        """Write address with zero balance to bad address file"""
        with self.lock:
            self._check_rotation(self.bad_address_file)
            
            with open(self.bad_address_file, 'a', encoding='utf-8') as f:
                f.write(f"{address}\n")

class StateManager:
    """State persistence manager"""
    
    def __init__(self, state_file: str = "state.json"):
        self.state_file = state_file
        self.state = ScannerState()
        self.lock = threading.Lock()
        self._load_state()
    
    def _load_state(self):
        """Load state from file"""
        try:
            if Path(self.state_file).exists():
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.state = ScannerState(**data)
        except Exception as e:
            logging.warning(f"Failed to load state: {e}")
    
    def save_state(self):
        """Save current state to file"""
        with self.lock:
            try:
                with open(self.state_file, 'w') as f:
                    json.dump(asdict(self.state), f, indent=2)
            except Exception as e:
                logging.error(f"Failed to save state: {e}")
    
    def update_state(self, **kwargs):
        """Update state fields"""
        with self.lock:
            for key, value in kwargs.items():
                if hasattr(self.state, key):
                    setattr(self.state, key, value)
            self.save_state()

class TUI:
    """Terminal User Interface using blessed"""
    
    def __init__(self, scanner):
        self.scanner = scanner
        self.term = Terminal()
        self.running = True
        
    def display_status(self):
        """Display scanner status and statistics"""
        with self.term.fullscreen(), self.term.hidden_cursor():
            while self.running:
                self.term.clear()
                
                # Header
                print(self.term.bold_blue("Bitcoin Legacy Wallet Scanner"))
                print(self.term.blue("=" * 50))
                print()
                
                # Status
                status = "Running" if self.scanner.state.is_running else "Paused"
                status_color = self.term.green if self.scanner.state.is_running else self.term.yellow
                print(f"Status: {status_color(status)}")
                print()
                
                # Statistics
                print(f"Generated: {self.scanner.state.last_generated:,}")
                print(f"Checked: {self.scanner.state.last_checked:,}")
                print(f"Found with balance: {self.scanner.state.last_found_with_balance:,}")
                print()
                
                # Performance
                if self.scanner.state.start_time > 0:
                    elapsed = time.time() - self.scanner.state.start_time
                    if elapsed > 0:
                        gen_rate = self.scanner.state.last_generated / (elapsed / 60)
                        check_rate = self.scanner.state.last_checked / (elapsed / 60)
                        print(f"Generation rate: {gen_rate:,.0f} addr/min")
                        print(f"Check rate: {check_rate:,.0f} addr/min")
                        print()
                
                # Controls
                print(self.term.bold("Controls:"))
                print("s - Start/Resume")
                print("p - Pause")
                print("q - Quit")
                print()
                
                # Queue info
                print(f"Generation queue: {self.scanner.gen_queue.qsize()}")
                print(f"RPC queue: {self.scanner.rpc_queue.qsize()}")
                
                # Wait for input
                with self.term.cbreak():
                    key = self.term.inkey(timeout=1.0)
                    if key:
                        if key.lower() == 's':
                            self.scanner.start()
                        elif key.lower() == 'p':
                            self.scanner.pause()
                        elif key.lower() == 'q':
                            self.scanner.stop()
                            self.running = False
                
                time.sleep(0.1)

class BitcoinLegacyScanner:
    """Main scanner class coordinating all components"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.state = StateManager()
        
        # Queues
        self.gen_queue = Queue(maxsize=self.config.get('queue_max', 100000))
        self.rpc_queue = Queue(maxsize=self.config.get('queue_max', 100000))
        
        # Components
        self.key_generator = KeyGenerator(self.config.get('batch_size', 512))
        self.rpc_scanner = BitcoinRPCScanner(self.config)
        self.output_writer = OutputWriter(
            self.config.get('output_dir', './out'),
            self.config.get('rotate_size_mb', 100)
        )
        
        # Workers
        self.gen_workers = self.config.get('gen_workers', mp.cpu_count())
        self.rpc_workers = self.config.get('rpc_workers', 4)
        
        # Control
        self.running = False
        self.paused = False
        self.stopping = False
        
        # Statistics
        self.stats = {
            'generated': 0,
            'checked': 0,
            'found_with_balance': 0,
            'start_time': 0,
            'last_gen_rate': 0,
            'last_check_rate': 0
        }
        
        # Threads
        self.gen_threads = []
        self.rpc_threads = []
        self.stats_thread = None
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        default_config = {
            'batch_size': 512,
            'gen_workers': 'auto',
            'rpc_workers': 'auto',
            'queue_max': 100000,
            'bitcoin_cli_path': 'bitcoin-cli',
            'network': 'mainnet',
            'rpc_timeout_sec': 120,
            'log_level': 'INFO',
            'output_dir': './out',
            'rotate_size_mb': 100
        }
        
        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
        except Exception as e:
            logging.warning(f"Failed to load config: {e}")
        
        # Auto-detect workers
        if default_config['gen_workers'] == 'auto':
            default_config['gen_workers'] = mp.cpu_count()
        if default_config['rpc_workers'] == 'auto':
            default_config['rpc_workers'] = 4
        
        return default_config
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scanner.log'),
                logging.StreamHandler()
            ]
        )
    
    def _signal_handler(self, signum, frame):
        """Handle system signals"""
        logging.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start the scanner"""
        if self.running and not self.paused:
            return
        
        if self.paused:
            self.paused = False
            logging.info("Scanner resumed")
        else:
            self.running = True
            self.stats['start_time'] = time.time()
            self.state.update_state(
                is_running=True,
                is_paused=False,
                start_time=self.stats['start_time']
            )
            logging.info("Scanner started")
            
            # Start worker threads
            self._start_workers()
    
    def pause(self):
        """Pause the scanner"""
        if not self.running or self.paused:
            return
        
        self.paused = True
        self.state.update_state(is_paused=True)
        logging.info("Scanner paused")
    
    def stop(self):
        """Stop the scanner"""
        if not self.running:
            return
        
        self.stopping = True
        self.running = False
        self.paused = False
        
        self.state.update_state(
            is_running=False,
            is_paused=False
        )
        
        logging.info("Scanner stopping...")
        
        # Wait for threads to finish
        for thread in self.gen_threads + self.rpc_threads:
            if thread.is_alive():
                thread.join(timeout=5.0)
        
        logging.info("Scanner stopped")
    
    def _start_workers(self):
        """Start worker threads"""
        # Start generation workers
        for _ in range(self.gen_workers):
            thread = threading.Thread(target=self._generation_worker, daemon=True)
            thread.start()
            self.gen_threads.append(thread)
        
        # Start RPC workers
        for _ in range(self.rpc_workers):
            thread = threading.Thread(target=self._rpc_worker, daemon=True)
            thread.start()
            self.rpc_threads.append(thread)
        
        # Start stats thread
        self.stats_thread = threading.Thread(target=self._stats_worker, daemon=True)
        self.stats_thread.start()
    
    def _generation_worker(self):
        """Worker thread for generating wallet keys"""
        while self.running and not self.stopping:
            if self.paused:
                time.sleep(0.1)
                continue
            
            try:
                # Generate batch
                wallets = self.key_generator.generate_batch()
                
                # Put in queue
                for wallet in wallets:
                    if self.stopping:
                        break
                    
                    try:
                        self.gen_queue.put(wallet, timeout=1.0)
                        self.stats['generated'] += 1
                    except:
                        break
                
                # Small delay to prevent overwhelming
                time.sleep(0.01)
                
            except Exception as e:
                logging.error(f"Generation worker error: {e}")
                time.sleep(1.0)
    
    def _rpc_worker(self):
        """Worker thread for RPC balance checking"""
        while self.running and not self.stopping:
            if self.paused:
                time.sleep(0.1)
                continue
            
            try:
                # Collect addresses for batch
                addresses = []
                wallets = []
                
                # Get addresses from generation queue
                while len(addresses) < self.config['batch_size'] and not self.stopping:
                    try:
                        wallet = self.gen_queue.get(timeout=0.1)
                        addresses.append(wallet.address)
                        wallets.append(wallet)
                    except Empty:
                        break
                
                if not addresses:
                    time.sleep(0.1)
                    continue
                
                # Check balances
                balances = self.rpc_scanner.scan_addresses(addresses)
                
                # Process results
                for wallet in wallets:
                    if self.stopping:
                        break
                    
                    balance = balances.get(wallet.address, 0)
                    wallet.balance_sats = balance
                    
                    if balance > 0:
                        self.output_writer.write_balance(wallet)
                        self.stats['found_with_balance'] += 1
                    else:
                        self.output_writer.write_bad_address(wallet.address)
                    
                    self.stats['checked'] += 1
                
            except Exception as e:
                logging.error(f"RPC worker error: {e}")
                time.sleep(1.0)
    
    def _stats_worker(self):
        """Worker thread for updating statistics"""
        while self.running and not self.stopping:
            try:
                # Update state
                self.state.update_state(
                    last_generated=self.stats['generated'],
                    last_checked=self.stats['checked'],
                    found_with_balance=self.stats['found_with_balance']
                )
                
                # Calculate rates
                if self.stats['start_time'] > 0:
                    elapsed = time.time() - self.stats['start_time']
                    if elapsed > 0:
                        self.stats['last_gen_rate'] = self.stats['generated'] / (elapsed / 60)
                        self.stats['last_check_rate'] = self.stats['checked'] / (elapsed / 60)
                
                time.sleep(5.0)  # Update every 5 seconds
                
            except Exception as e:
                logging.error(f"Stats worker error: {e}")
                time.sleep(5.0)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Bitcoin Legacy Wallet Scanner")
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--start', action='store_true', help='Start scanning immediately')
    parser.add_argument('--pause', action='store_true', help='Pause scanning')
    parser.add_argument('--resume', action='store_true', help='Resume scanning')
    parser.add_argument('--headless', action='store_true', help='Run without TUI')
    parser.add_argument('--duration', type=int, help='Run for specified seconds then stop')
    parser.add_argument('--dry-run', action='store_true', help='Generate keys but mock balance checks')
    parser.add_argument('--output-dir', help='Output directory')
    parser.add_argument('--batch-size', type=int, help='Batch size for RPC calls')
    parser.add_argument('--gen-workers', type=int, help='Number of generation workers')
    parser.add_argument('--rpc-workers', type=int, help='Number of RPC workers')
    
    args = parser.parse_args()
    
    # Create scanner
    scanner = BitcoinLegacyScanner(args.config)
    
    # Override config with CLI args
    if args.output_dir:
        scanner.config['output_dir'] = args.output_dir
    if args.batch_size:
        scanner.config['batch_size'] = args.batch_size
    if args.gen_workers:
        scanner.config['gen_workers'] = args.gen_workers
    if args.rpc_workers:
        scanner.config['rpc_workers'] = args.rpc_workers
    
    # Handle CLI commands
    if args.start:
        scanner.start()
    elif args.pause:
        scanner.pause()
    elif args.resume:
        scanner.start()
    
    # Run mode
    if args.headless:
        # Headless mode
        if args.start:
            if args.duration:
                time.sleep(args.duration)
                scanner.stop()
            else:
                # Keep running until interrupted
                try:
                    while scanner.running:
                        time.sleep(1.0)
                except KeyboardInterrupt:
                    scanner.stop()
    else:
        # TUI mode
        tui = TUI(scanner)
        if args.start:
            scanner.start()
        tui.display_status()
    
    # Cleanup
    scanner.stop()

if __name__ == "__main__":
    main()
