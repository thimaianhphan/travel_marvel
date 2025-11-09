# TravelMarvel

Getting started
---------------

1. Clone the repository:

```bash
git clone https://github.com/thimaianhphan/travel_marvel.git
cd cassini-ai-travel-agent
```

2. Create and activate a Python virtual environment (recommended):

On macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

Upgrade pip (optional)
```bash
python -m pip install --upgrade pip
```

Install all packages from requirements.txt

```bash
pip install -r requirements.txt
```

Running the application (development)
-------------------------------------
1. Backend

To run the FastAPI application locally, use the following command (from the project root). Make sure you are in the virtual environment if you created one.

```bash
fastapi dev backend/app.py

```

2. Frontend

Install dependencies and start the client from the `frontend` directory:

```bash
cd frontend
npm install
npm run dev
```

Map thumbnails now use Mapbox Static Images. Create a `.env.local` file in `frontend/` with your token:

```
NEXT_PUBLIC_MAPBOX_TOKEN=pk.your-token-here
```

Without the token, thumbnails fall back to a simple placeholder.