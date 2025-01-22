from quart import Quart, request, jsonify, render_template
import aiohttp
import asyncio
from quart_cors import cors  # Import quart_cors for CORS support
#from qwen_deepseek1_5 import TextGenerator 

app = Quart(__name__)
app = cors(app, allow_origin="*")  # Allow all origins; adjust as needed for security

from transformers import pipeline

class TextGenerator:
	def __init__(self, model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"):
		"""Initialize the text generation pipeline with a given model."""
		self.pipeline = pipeline(
			"text-generation",
			model=model
		)

	def generate(self, input_text, max_length=100, num_return_sequences=1, top_k=50, top_p=0.95, temperature=0.7, pad_token_id=50256):
		"""Generate text based on input with customizable parameters."""
		response = self.pipeline(
			input_text,
			max_length=max_length,
			num_return_sequences=num_return_sequences,
			top_k=top_k,
			top_p=top_p,
			temperature=temperature,
			pad_token_id=pad_token_id
		)
		return response




class MoleculeDataFetcher:
	BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

	async def search_molecules(self, query, max_results=100):
		url = f"{self.BASE_URL}/compound/name/{query}/cids/JSON"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				if response.status == 200:
					data = await response.json()
					return data.get('IdentifierList', {}).get('CID', [])[:max_results]
				else:
					response.raise_for_status()

	async def fetch_smiles(self, molecule_id):
		url = f"{self.BASE_URL}/compound/cid/{molecule_id}/property/CanonicalSMILES/JSON"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				if response.status == 200:
					data = await response.json()
					properties = data.get('PropertyTable', {}).get('Properties', [])
					if properties:
						return properties[0].get('CanonicalSMILES')
				else:
					response.raise_for_status()

	async def fetch_structure(self, molecule_id, format_type='JSON'):
		url = f"{self.BASE_URL}/compound/cid/{molecule_id}/record/{format_type}"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				if response.status == 200:
					return await response.json() if format_type == 'JSON' else await response.read()
				else:
					response.raise_for_status()

	async def search_similar_molecules(self, smiles, threshold=70, max_results=10):
		url = f"{self.BASE_URL}/compound/similarity/smiles/{smiles}/JSON?Threshold={threshold}&MaxRecords={max_results}"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				if response.status == 202:
					list_key = (await response.json()).get("Waiting", {}).get("ListKey")

					# Polling
					poll_url = f"{self.BASE_URL}/compound/listkey/{list_key}/cids/JSON"
					while True:
						async with session.get(poll_url) as poll_response:
							if poll_response.status == 200:
								data = await poll_response.json()
								return data.get('IdentifierList', {}).get('CID', [])[:max_results]
							elif poll_response.status != 202:
								poll_response.raise_for_status()
							await asyncio.sleep(5)
				else:
					response.raise_for_status()

	async def fetch_molecule_properties(self, molecule_id):
		url = f"{self.BASE_URL}/compound/cid/{molecule_id}/property/MolecularFormula,MolecularWeight,IUPACName,ExactMass,MonoisotopicMass,TPSA,XLogP,Complexity,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,Charge,InChI,InChIKey,CanonicalSMILES,IsomericSMILES/JSON"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				if response.status == 200:
					data = await response.json()
					properties = data.get('PropertyTable', {}).get('Properties', [])
					if properties:
						return properties[0]
				else:
					response.raise_for_status()

fetcher = MoleculeDataFetcher()

@app.route('/', methods=['GET', 'POST'])
async def index():
	if request.method == 'POST':
		try:
			print("POST request received")
			form = await request.form
			smiles = form['smiles']
			print(f"SMILES input: {smiles}")
			
			similar_molecule_ids = await fetcher.search_similar_molecules(smiles)
			print(f"Similar molecule IDs: {similar_molecule_ids}")
			
			molecules = []
			
			for mid in similar_molecule_ids:
				print(f"Processing molecule ID: {mid}")
				try:
					# Generate and print the response
					
					smiles = await fetcher.fetch_smiles(mid)
					print(f"Fetched SMILES: {smiles}")
					properties = await fetcher.fetch_molecule_properties(mid)
					print(f"Fetched properties: {properties}")
					molecules.append({
						'id': mid,
						'smiles': smiles,
						'properties': properties
					})
				except Exception as e:
					print(f"Error processing molecule {mid}: {str(e)}")
			
			if not molecules:
				print("Molecules list is empty or None!")
			else:
				print(f"Successfully processed {len(molecules)} molecules")
				
			return await render_template('index.html', molecules=molecules)
		except Exception as e:
			print(f"Error in route handler: {str(e)}")
			raise
			
	return await render_template('index.html')

@app.route('/molecule/<int:molecule_id>')
async def view_molecule(molecule_id):
	smiles = await fetcher.fetch_smiles(molecule_id)
	properties = await fetcher.fetch_molecule_properties(molecule_id)		
	return jsonify({'smiles': smiles, 'properties': properties})

if __name__ == '__main__':
	app.run(debug=True)
