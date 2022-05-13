import json
from posixpath import abspath, dirname
import xml.etree.ElementTree as ET
import asyncio
import aiohttp

async def main():
    AssetId = input('Enter in the AssetID: ')

    async with aiohttp.ClientSession() as session:
        print('Getting asset info')

        async def Get(Url):
            async with session.get(url=Url) as resp:
                body = await resp.text()
                return body

        async def GetRaw(Url):
            async with session.get(url=Url) as resp:
                body = await resp.read()
                return body
        
        AssetInfoResponse = await Get(f'https://assetdelivery.roblox.com/v2/assetId/{AssetId}') # Get the asset info
        if (AssetInfoResponse is None):
            return print('Couldn\'t fetch asset info') # No response

        AssetInfoJSON = (json.loads(AssetInfoResponse)) # Decode the json

        if (AssetInfoJSON.get('errors')): # if there are any errors, raise an exception
            return print(f"Error Code {AssetInfoJSON.get('errors')[0].get('code')}: {AssetInfoJSON.get('errors')[0].get('message')}")
        
        print('Getting image location from XML')
        if (AssetInfoJSON.get('locations')): # assuming the 1st index has the actual location we need
            location = AssetInfoJSON.get('locations')[0].get('location')
            AssetXML = await Get(location) # this is an XML file

            # Roblox stores instances as (basically) XML files, and can be parsed as one.
            # Here we are reading the XML data in order to find the location of the URL for the pants

            if (AssetXML is None):
                return print('Couldn\'t fetch XML') # XML is None
            
            root = ET.fromstring(AssetXML) # Get the XML root

            i = 0
            for url in root.iter('url'):
                i += 1
                ImageURL = url.text # We found the image URL
                print(f'Found {ImageURL}')
                
                ImageId = ImageURL.replace('http://www.roblox.com/asset/?id=', '') # Get the image id by removing request url
                print(f'Is is {ImageId}')

                imgdata = await GetRaw(f'https://assetdelivery.roblox.com/v1/asset/?id={ImageId}') # get image data

                f = open(f'{dirname(abspath(__file__))}/{AssetId}-{i}.png', 'wb') # open da file
                f.write(imgdata) # write the data from the image

                print(f'Saved file as {AssetId}\-{i}.png')

                f.close()

            await session.close() # close the session
            


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
