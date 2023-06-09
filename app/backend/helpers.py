import json
from fastapi.responses import Response
from fastapi.encoders import jsonable_encoder
from app.app import app

async def download_json(token: str):
    filename = "setting.json"
    state = app.state_manager.get_state(token)
    data = jsonable_encoder(state.substates['paperspace_state'].environments)
    data = json.dumps(data, indent=4)
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "application/json",
    }
    
    return Response(content=data, headers=headers)