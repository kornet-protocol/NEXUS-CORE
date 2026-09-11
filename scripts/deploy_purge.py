"""
deploy_purge.py
===============
Скрипт деплоя Контракта Очищения и Founding Purger SBT.

Зависимости: web3, eth-account, python-dotenv
Конфигурация: Foundry (forge build) + .env
"""

import json
import os
import sys
from pathlib import Path

from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")
NEXUS_TREASURY = os.getenv("NEXUS_TREASURY")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1"))

if not all([RPC_URL, PRIVATE_KEY, NEXUS_TREASURY]):
    print("ERROR: Missing required environment variables: RPC_URL, DEPLOYER_PRIVATE_KEY, NEXUS_TREASURY")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print(f"ERROR: Cannot connect to RPC {RPC_URL}")
    sys.exit(1)

account = Account.from_key(PRIVATE_KEY)
print(f"Deployer: {account.address}")
print(f"Chain ID: {CHAIN_ID}")
print(f"Balance: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} ETH")


def load_artifact(contract_name: str) -> dict:
    base = Path(__file__).resolve().parent.parent / "smart-contracts" / "out"
    candidates = [
        base / f"{contract_name}.dbg.json",
        base / contract_name / f"{contract_name}.json",
    ]
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(
        f"Artifact not found for {contract_name}. Run 'forge build' first. "
        f"Checked: {[str(p) for p in candidates]}"
    )


def deploy_founding_purger() -> str:
    artifact = load_artifact("FoundingPurger")
    abi = artifact["abi"]
    bytecode = artifact["bytecode"]["object"]

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = contract.constructor(NEXUS_TREASURY).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 2_000_000,
        "gasPrice": w3.eth.gas_price,
        "chainId": CHAIN_ID,
    })

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"FoundingPurger deployed at: {receipt.contractAddress}")
    return receipt.contractAddress


def deploy_purge_contract(founding_purger_address: str) -> str:
    artifact = load_artifact("PurgeContract")
    abi = artifact["abi"]
    bytecode = artifact["bytecode"]["object"]

    usdc = os.getenv("USDC_ADDRESS", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    usdt = os.getenv("USDT_ADDRESS", "0xdAC17F958D2ee523a2206206994597C13D831ec7")
    dex_aggregator = os.getenv("DEX_AGGREGATOR", "0x111111125421cA6dc452d289314280a0f8842A65")

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = contract.constructor(
        usdc,
        usdt,
        founding_purger_address,
        NEXUS_TREASURY,
        dex_aggregator
    ).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 3_000_000,
        "gasPrice": w3.eth.gas_price,
        "chainId": CHAIN_ID,
    })

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"PurgeContract deployed at: {receipt.contractAddress}")
    return receipt.contractAddress


def whitelist_initial_tokens(purge_contract_address: str, tokens: list[str]) -> None:
    artifact = load_artifact("PurgeContract")
    abi = artifact["abi"]
    contract = w3.eth.contract(address=purge_contract_address, abi=abi)

    for token in tokens:
        tx = contract.functions.addSupportedToken(token).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 100_000,
            "gasPrice": w3.eth.gas_price,
            "chainId": CHAIN_ID,
        })
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Whitelisted: {token}")


if __name__ == "__main__":
    print("Deploying NEXUS Purge Infrastructure...")
    purger = deploy_founding_purger()
    purge = deploy_purge_contract(purger)
    initial_tokens = [
        token.strip()
        for token in os.getenv("INITIAL_SUPPORTED_TOKENS", "").split(",")
        if token.strip()
    ]
    if initial_tokens:
        whitelist_initial_tokens(purge, initial_tokens)
    print("Deployment complete.")
