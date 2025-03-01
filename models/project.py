from pydantic import BaseModel

class Project(BaseModel):
    name: str
    price: str
    bidding_time: str
    winning_time: str
    scrapping_time: str
    description: str

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