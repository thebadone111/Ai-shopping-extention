import logging
import openai
import requests
import json
import time
import asyncio
from functools import partial


# create a custom formatter
log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(module)s: %(message)s')
logger = logging.getLogger(__name__)

# create a logger and set the formatter
handler = logging.StreamHandler()
handler.setFormatter(log_formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def run_openai(body):
    prompt = body + ". Answer this by recommending one or more products found on amazon, and these parameters are required in the answer: The answer must only include product names separated by a newline. Products must be found on amazon. Do not use any other formating other than the one explained above. \nBefore replying, validate that the answer follows the rules explained above.\n"
    openai_api_key = "api_key"
    model = "text-davinci-003"
    max_tokens = 500
    temp = 0.6
    openai.api_key = openai_api_key
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temp
    )
    text = response["choices"][0]["text"]
    return text

async def get_affiliate(product):
    return_dict = {}
    final_a_link = ""
    img_link = ""
    price = ""
    rating = ""
    api_key = "api_key"
    params = {
        'api_key': api_key,
        'type': 'search',
        'amazon_domain': 'amazon.com',
        'search_term': product,
        'sort_by': 'featured',
        'exclude_sponsored': 'false',
        'max_page': '1',
        'output': 'json',
        'include_html': 'false',
        'associate_id': 'shoppingai0e-20'
    }
    logger.info("Getting link for : %s", product)
    api_result = await asyncio.get_event_loop().run_in_executor(None, requests.get, 'https://api.rainforestapi.com/request', params)
    if api_result.status_code != 200:
        logger.error("Product query returned error: ",api_result.status_code, api_result)
        return_dict.update({
            "title": product,
            "link": "",
            "img_link": "",
            "price": "",
            "rating": ""
        })
        return return_dict
    
    temp = api_result.json()

    try:
        final_a_link = temp["search_results"][0]["link"]
    except:
        final_a_link = ""
        logger.error("Link not found")

    try:
        img_link = temp["search_results"][0]["image"]
    except:
        img_link = ""
        logger.error("Image link not found")

    try:
        price = temp["search_results"][0]["price"]["raw"]
    except:
        price = ""
        logger.error("Price not found")

    try:
        rating = str(temp["search_results"][0]["rating"])
    except:
        rating = ""
        logger.error("Ratings not found")

    return_dict.update({
        "title": product,
        "link": final_a_link,
        "img_link": img_link,
        "price": price,
        "rating": rating
    })
    logger.info("Done with product: %s", product)
    return return_dict

async def round_two(p_string):
    temp = 0.35
    openai.api_key = "api_key"
    logger.info("Starting round 2")
    msg = [
                {"role": "system", "content": "You are an api which takes in product names and sends back a review for each product, the response is in the JSON formatting: RFC8259"},
                
                {"role": "user", "content": "Write an explanation and review of these products: 'Slime making kit ', 'Fujifilm Instax Mini 9 Instant Camera ', 'Special Edition Monopoly Game'"},
                {"role": "assistant", "content": "{\"product-1-review\": \"The Slime Making Kit is a great gift for any child. It comes with all the supplies needed to make a variety of fun and colorful slime! It's a great way to encourage creativity, as kids can mix and match colors and ingredients to create their own unique creations. Plus, it's a great way to keep them busy for hours!\",\n \n \"product-2-review\": \"The Fujifilm Instax Mini 9 is the perfect way to capture special memories with your sister. It's a great instant camera with a cute, retro design and produces high-quality photos that are perfect for framing and displaying. It's a fun and easy way to take great photos and create lasting memories!\",\n \n \"product-3-review\": \"This special edition Monopoly game is a great way to get your sister and her friends together for a fun game night. This game includes all the classic Monopoly pieces and is great for teaching kids about economics and strategy. Plus, the pieces and board are of great quality and will last for years!\"}"},
                
                {"role": "user", "content": "Write an explanation and review of these products: Thermos Vacuum Insulated Bottle, Tafco Stainless Steel Water Bottle"},
                {"role": "assistant", "content": "{\"product-1-review\": \"The Thermos Vacuum Insulated Bottle is a great choice for anyone who wants to keep their beverages hot or cold for extended periods of time. Its vacuum insulation technology ensures that your drink stays at the desired temperature for up to 24 hours, making it perfect for long hikes, camping trips, or just a day at the office. It's also made of durable stainless steel and has a convenient carrying handle, making it easy to take with you wherever you go.\",\"product-2-review\": \"The Tafco Stainless Steel Water Bottle is a stylish and practical choice for anyone who wants to stay hydrated on the go. It's made of high-quality stainless steel, which is both durable and easy to clean. Its double-walled insulation keeps your drink cold for up to 24 hours, making it perfect for hot summer days or long workouts. It also has a convenient flip-top lid that makes it easy to drink from and prevents spills.\"}"},
    
                {"role": "user", "content": "Write an explanation and review of these products: " + p_string}
            ]
    response = await asyncio.get_event_loop().run_in_executor(None, partial(openai.ChatCompletion.create, model="gpt-3.5-turbo", temperature=temp, messages=msg))
    text = response["choices"][0]["message"]["content"]
    try:
        text = json.loads(text)
    except:
        if text.endswith("}"):
            logger.error("Failed to make json: %s", text)
        else:
            pos = text.rfind("}")
            text = text[:pos]
            try:
                text = json.loads(text)
                return text
            except:
                logger.error("Failsafe did not work, cannot convert answer to json: %s", text)
                return "error"
    logger.info("Done with round 2")
    return text

async def main(prompt):
    s = time.time()
    logger.info("Request received: %s", prompt)
    products = run_openai(prompt)
    logger.info("Products found: %s", products)
    arr = products.split("\n")
    arr.pop(0)

    while len(arr) > 5:
        arr.pop(-1)

    logger.info("Arr lenght: %s \n Arr: %s", len(arr), arr)

    task_list = []
    for product in arr:
        task_list.append(asyncio.create_task(get_affiliate(product)))
    task_list.append(asyncio.create_task(round_two(products)))
    logger.info("tasks added")
    results = await asyncio.gather(*task_list)
    if results != "error":
        for i in range(0, len(results)-1):
            try:
                results[i]["review"] = results[-1]["product-"+str(i+1)+"-review"]
            except:
                logger.error(f"failed to move the results into the dict. At: {i}")
                logger.error(results)
                continue
        results.remove(results[-1])
        e = time.time()
        logger.info("Time: %s \n", e-s)
        return results
    else:
        logger.error("Returning error to server", results)
        return "error"