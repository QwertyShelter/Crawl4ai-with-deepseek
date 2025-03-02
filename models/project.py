from pydantic import BaseModel

class Project_base(BaseModel):
    Location: str
    Title: str
    No: str
    Company: str
    Price: str

class Project_adv(BaseModel):
    Brand: str
    Model: str
    Winning_time: str

CSV_HEAD = [
    "Location",
    "Title",
    "No",
    "Company",
    "Price",
    "Brand",
    "Model",
    "Winning_time"
]

'''
SCHEMA = {
    "name": "Wedding Extractor",
    "baseSelector": "[class^='info-container--d187a']",
    "fields": [
        {
            "name": "name",
            "selector": "[class^='vendor-name--a628b']",
            "type": "text",
        },
        {
            "name": "price",
            "selector": "[class^='secondary-info-container--76d09']",
            "type": "text",
        },
        {
            "name": "description",
            "selector": "[class^='container--38c42']",
            "type": "text",
        },
    ],
}
'''