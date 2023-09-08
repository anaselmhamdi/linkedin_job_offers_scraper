import json
import os
import uuid

import boto3
import requests
from bs4 import BeautifulSoup

SOFTWARE_ENGINEER_FRANCE_JOB_SEARCH = "https://www.linkedin.com/jobs/search?keywords=Software%20Engineer&location=France&locationId=&geoId=105015875&f_TPR=r86400&position=1&pageNum=0"

MAX_RETRIES = 3


def get_current_ip():
    return requests.get("http://checkip.amazonaws.com").text.rstrip()


def scrape_job_offer(event, context):
    job_offer_url = event.get("url")
    response = requests.get(job_offer_url)
    soup = BeautifulSoup(response.text, "html.parser")
    offer_json = soup.select_one('script[type="application/ld+json"]')
    if offer_json:
        offer = json.loads(offer_json.get_text(strip=True))
        offer["ip_used_to_scrape"] = get_current_ip()
        return {"statusCode": 200, "body": offer}
    else:
        return {"statusCode": 500, "body": "Job offer not found"}


def scrape_job_urls(event, context):
    JOB_OFFER_SCRAPER_ARN = os.environ["JOB_OFFER_SCRAPER_ARN"]
    response = requests.get(SOFTWARE_ENGINEER_FRANCE_JOB_SEARCH)
    soup = BeautifulSoup(response.text, "html.parser")
    job_offer_urls = [offer.a["href"] for offer in soup.select("ul.jobs-search__results-list > li")]
    client = boto3.client("lambda")
    results = []
    for job_offer_url in job_offer_urls:
        payload = {"url": job_offer_url}
        lambda_response = client.invoke(
            FunctionName=JOB_OFFER_SCRAPER_ARN,
            InvocationType="RequestResponse",
            Payload=bytes(json.dumps((payload)), "utf-8"),
        )
        response = json.loads(lambda_response["Payload"].read().decode())
        status_code = response["statusCode"]
        if status_code == 200:
            results.append(response["body"])
        else:
            # Reset the lambda to get a new IP address
            client.update_function_configuration(
                FunctionName=JOB_OFFER_SCRAPER_ARN,
                Environment={"Variables": {"RANDOM_HASH_TO_FORCE_COLD_START": str(uuid.uuid4())}},
            )
            waiter = client.get_waiter("function_updated")
            waiter.wait(FunctionName=JOB_OFFER_SCRAPER_ARN)
            lambda_response = client.invoke(
                FunctionName=JOB_OFFER_SCRAPER_ARN,
                InvocationType="RequestResponse",
                Payload=bytes(json.dumps((payload)), "utf-8"),
            )
            response = json.loads(lambda_response["Payload"].read().decode())
            results.append(response["body"])
    return results
