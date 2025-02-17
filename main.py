from fastapi import FastAPI, HTTPException
import json
import requests
from web3 import Web3

# Configuration Blockchain
INFURA_URL = "https://sepolia.infura.io/v3/TON_INFURA_PROJECT_ID"
CONTRACT_ADDRESS = "0xTonSmartContractAddress"
PRIVATE_KEY = "0xTaClePrivee"
ACCOUNT_ADDRESS = "0xTonAdresseEthereum"

# Connexion à la blockchain
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
if not web3.is_connected():
    raise Exception("Échec de connexion à Ethereum")

# Charger ABI du Smart Contract
with open("contract_abi.json", "s") as abi_file:
    contract_abi = json.load(abi_file)
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# Initialiser FastAPI
app = FastAPI()

@app.post("/receive-data/")
def receive_data(payload: dict):
    try:
        # Extraire les données reçues de Datacake
        device_id = payload.get("device_id")
        temperature = payload.get("temperature")
        humidity = payload.get("humidity")
        timestamp = payload.get("timestamp")
        
        if not device_id or temperature is None or humidity is None:
            raise HTTPException(status_code=400, detail="Données incomplètes")
        
        # Préparer la transaction blockchain
        nonce = web3.eth.get_transaction_count(ACCOUNT_ADDRESS)
        txn = contract.functions.storeData(device_id, temperature, humidity, timestamp).build_transaction({
            'from': ACCOUNT_ADDRESS,
            'gas': 2000000,
            'gasPrice': web3.to_wei('10', 'gwei'),
            'nonce': nonce
        })
        
        # Signer et envoyer la transaction
        signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return {"message": "Données envoyées à la blockchain", "tx_hash": tx_hash.hex()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-latest-data/{device_id}")
def get_latest_data(device_id: str):
    try:
        data = contract.functions.getLatestData(device_id).call()
        return {
            "device_id": device_id,
            "temperature": data[0],
            "humidity": data[1],
            "timestamp": data[2]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
