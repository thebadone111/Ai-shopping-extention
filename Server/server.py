from fastapi import FastAPI, Request
import uvicorn
import asyncio
import pymysql
from datetime import datetime
import logging
from main import main


# create a custom formatter
log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(module)s: %(message)s')
logger = logging.getLogger(__name__)

# create a logger and set the formatter
handler = logging.StreamHandler()
handler.setFormatter(log_formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def database(user_id, result, prompt):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='pass',
        database='main'
    )

    client_prompt = prompt
    productNames = []
    productLinks = []
    productReviews = []
    productPrices = []
    timestamp = datetime.now()

    try:
        for x in range(0, len(result) - 1):
            productNames.append(result[x]["title"])
            productLinks.append(result[x]["link"])
            productReviews.append(result[x]["review"])
            productPrices.append(result[x]["price"])
        productNames = ",".join(productNames)
        productLinks = ",".join(productLinks)
        productReviews = ",".join(productReviews)
        productPrices = ",".join(productPrices)
    except Exception as e:
        logger.error(f"Error: {e}")

    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO data (user_id, client_prompt, timestamp, products_recommended, links_to_products, price_for_products, recommendation_text) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (user_id, client_prompt, timestamp, productNames, productLinks, productPrices, productReviews)
            cursor.execute(sql, val)
            conn.commit()
            logger.info("Data added into database")
    except Exception as e:
        logger.error(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

app = FastAPI()

@app.get('/')
async def index(request: Request):
    param = request.query_params.get('param')
    try:
        param = param.split("?")
    except:
        return "error"
    prompt = param[0]
    user_id = param[1].replace("user_id=", "")
    task = asyncio.create_task(main(prompt))
    result = await task
    if result == "error":
        logger.error("Returning error to client")
        return "error"
    try:
        database(user_id, result, prompt)
    except Exception as e:
        logger.error(f"Problem with database: {e}")
    return result

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)