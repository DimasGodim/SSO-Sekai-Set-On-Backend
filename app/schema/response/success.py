from typing import Optional
def success(data: dict, pesan: Optional[str] = "None"):
    return {
        "message":  pesan,
        "data": data
    }