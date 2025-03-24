import aiohttp
import asyncio

async def download_file(link:str, output_path:str="downloaded_file_path.pdf")->str: # select the output file path and type based on the file type.
    """
    Asynchronously download a file from the given link and save it to the output path.

    Args:
        link (str): URL to the file
        output_path (str): Path to save the downloaded file

    Returns:
        output_path (str): Path to the downloaded file
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link, timeout=10000) as response:
                if response.status == 200:
                    pdf_content = await response.read()  # Asynchronously read response
                    with open(output_path, "wb") as f:
                        f.write(pdf_content)
                    return output_path
                else:
                    print(f"Failed to download file. HTTP Status: {response.status}")
                    return None
    except aiohttp.ClientError as e:
        print(f"Error in downloading file: {e}")
        return None

if __name__=="__main__":
    # url = "https://www.yonkersny.gov/DocumentCenter/View/14086/Zoning-Board-of-Appeals--RESOLUTION-OF-APPROVAL-Case-5870-105-Ridgewood-Ave?bidId=" # example link

    ## reading a single pdf
    # asyncio.run(download_file(link=url, output_path="downloaded_file_path.pdf"))

    ## reading multiple pdfs from a json file containing the links. you can also use text, csv, or any other file format. adjust the code accordingly.
    import json
    with open("file_names.json", mode='r') as file:
        data = json.load(fp=file)
    print("Total pdfs", len(list(data)))
    async def main():
        tasks = [download_file(link=pdf['file_link'], output_path=f"{pdf['file_name']}.pdf") for pdf in data]
        await asyncio.gather(*tasks)
    asyncio.run(main())
