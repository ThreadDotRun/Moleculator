# Moleculator

Moleculator is a web-based molecular visualization tool that allows users to search for and view 3D representations of molecules using SMILES notation. The application leverages PubChem's API for molecular data retrieval and 3Dmol.js for interactive 3D visualization.

![Demo GIF](./static/demo.gif)

## Features

- Search molecules using SMILES notation
- View 3D molecular structures with interactive controls
- Display similar molecules based on structural similarity
- Show detailed molecular properties including:
  - Molecular Formula
  - Molecular Weight
  - IUPAC Name
  - Exact Mass
  - Monoisotopic Mass
  - TPSA
  - XLogP
  - Complexity
  - H-Bond Donor/Acceptor Count
  - Rotatable Bond Count
  - Various chemical identifiers (InChI, InChIKey, SMILES)

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ThreadDotRun/moleculator.git
cd moleculator
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install quart quart-cors aiohttp transformers
```

## Project Structure

```
moleculator/
├── app.py              # Main application file
├── static/
│   ├── styles.css      # CSS styles
│   └── spinner.gif     # Loading animation
├── templates/
│   └── index.html      # Main template file
└── README.md           # This file
```

## Usage

1. Start the server:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Enter a SMILES string in the search box (e.g., "CC(=O)OC1=CC=CC=C1C(=O)O" for Aspirin)

4. View the 3D structure and molecular properties of the searched molecule and similar compounds

## API Endpoints

- `GET /`: Main page with search interface
- `POST /`: Submit SMILES string for searching similar molecules
- `GET /molecule/<molecule_id>`: Get JSON data for a specific molecule

## Technologies Used

- Backend:
  - Quart (async Flask-like framework)
  - aiohttp for async HTTP requests
  - PubChem REST API
- Frontend:
  - 3Dmol.js for molecular visualization
  - jQuery for DOM manipulation
  - NCI Chemical Identifier Resolver for SMILES to MOL conversion

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PubChem for providing molecular data
- 3Dmol.js team for the visualization library
- NCI/CADD Group for the Chemical Identifier Resolver service

## Note

This application is for educational and research purposes only. Always verify molecular data with authoritative sources before using it in any critical applications.