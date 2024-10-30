import sys
import logging

# Add proto folder to path
sys.path.append("proto")

# Add the directory containing api.py and the proto directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'proto'))

import sys
import logging

import grpc
from scrape_pb2 import ScrapeRequest, ScrapeBlobRequest, ScrapeStatusRequest
from scrape_pb2_grpc import ScrapeServiceStub

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("grpc")
logger.setLevel(logging.DEBUG)

# Add proto folder to path
sys.path.append("proto")


def create_stub():
    """Create a gRPC stub (client)."""
    channel = grpc.insecure_channel("localhost:5200")
    return ScrapeServiceStub(channel)


def send_scrape_request(stub, name, url):
    """Send a scrape request and return the response."""
    request = ScrapeRequest(name=name, url=url)
    response = stub.Scrape(request)
    logger.info(f"ScrapeService response for {name}: {response.message}")
    return response


def check_scraping_status(stub, name):
    """Check if scraping is done and return the status."""
    status_request = ScrapeStatusRequest(name=name)
    try:
        status_response = stub.IsScrapingDone(status_request)
        logger.info(f"Is scraping done for {name}: {status_response.is_done}")
        return status_response.is_done
    except grpc.RpcError as e:
        logger.error(f"Failed to check scraping status for {name}: {e.details()}")
        return None


def get_scraping_blob(stub, name):
    """Get the scraping blob as JSON and return it."""
    blob_request = ScrapeBlobRequest(name=name)
    try:
        blob_response = stub.GetScrapingBlob(blob_request)
        logger.info(f"Scraping blob for {name}: {blob_response.json_blob}")
        return blob_response.json_blob
    except grpc.RpcError as e:
        logger.error(f"Failed to get scraping blob for {name}: {e.details()}")
        return None


def run():
    """Main function to run the gRPC client."""
    stub = create_stub()

    # Send scrape requests
    # send_scrape_request(stub, "EmbeddedOne", "http://embeddedone.com")
    # send_scrape_request(stub, "Soccentric", "http://soccentric.com")

    # Check scraping status and get blobs
    check_scraping_status(stub, "EmbeddedOne.com")
    get_scraping_blob(stub, "EmbeddedOne.com")

    check_scraping_status(stub, "soccentric.com")
    get_scraping_blob(stub, "soccentric.com")


if __name__ == "__main__":
    run()
