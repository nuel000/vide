from scrapingbee import ScrapingBeeClient
import sys

client = ScrapingBeeClient(api_key='NP63V99OC92MT0LQWVGA56GEH32NEZ183YIHJ6XNPBCDSMTCH06ZI38QYB1G5I47UUP44H4S141W0VA2')

response = client.get("https://web.facebook.com/ads/library/?active_status=all&ad_type=political_and_issue_ads&country=NG&id=1054028289359210&media_type=all")

print('Response HTTP Status Code: ', response.status_code)
sys.stdout.flush()
print('Response HTTP Response Body: ', response.content)
sys.stdout.flush()
