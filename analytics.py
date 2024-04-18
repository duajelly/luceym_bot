from aiohttp import ClientSession
import time

MEASUREMENT_ID = ''
API_SECRET = ''

async def send_analytics(user_id, user_lang_code, action_name):
    
    params = {
        'client_id': str(user_id),
        'user_id': str(user_id),
        'user_properties': {
            'mpCountry': {
                'value': "Russia"
            },
            'mpStatus': {
                'value': 'user'
            }
        },
        'events': [{
            'name': action_name,
            'params': {                
                'language': "ru",
                'engagement_time_msec': '1',
            }
        }],
    }
    async with ClientSession() as session:
        await session.post(
                f'https://www.google-analytics.com/'
                f'mp/collect?measurement_id={MEASUREMENT_ID}&api_secret={API_SECRET}',
                json=params)