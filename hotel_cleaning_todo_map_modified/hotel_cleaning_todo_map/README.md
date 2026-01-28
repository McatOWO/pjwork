# Hotel Cleaning ToDo (Map)

## Features
- Map with pins near relevant locations.
- Click a pin to open that task UI (camera -> Teachable Machine inference).
- perfect/good => OK (pin becomes ✅)
- bad => Fix required (pin becomes ❗, note required)
- Images are NOT uploaded or stored. Only results are saved in browser localStorage.

## Setup (Windows)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install flask
flask --app app run --debug
```

Open:
http://127.0.0.1:5000/

## Files
- static/room_map.png : room floor plan image
- static/model/ : teachable machine model files (model.json, metadata.json, weights.bin)
