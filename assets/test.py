import json
import asyncio
from functools import wraps
from request import request  # import our request function.

def wrapper(f):
	@wraps(f)
	def inner(*args, **kwargs):
		return asyncio.ensure_future(f(*args, **kwargs))
	return inner

@wrapper
async def test():
    print("Testing request.py")
    baseurl = "https://jsonplaceholder.typicode.com"

    # GET
    headers = {"Content-type": "application/json"}
    response = await request(f"{baseurl}/posts/2", method="GET", headers=headers)
    print(f"GET request=> status:{response.status}, json:{await response.json()}")

    # POST
    body = json.dumps({"title": "test_title", "body": "test body", "userId": 1})
    new_post = await request(f"{baseurl}/posts", body=body, method="POST", headers=headers)
    print(f"POST request=> status:{new_post.status}, json:{await new_post.json()}")

    # PUT
    body = json.dumps({"id": 1, "title": "test_title", "body": "test body", "userId": 2})
    new_post = await request(f"{baseurl}/posts/1", body=body, method="PUT", headers=headers)
    print(f"PUT request=> status:{new_post.status}, json:{await new_post.json()}")

    # DELETE
    new_post = await request(f"{baseurl}/posts/1", method="DELETE", headers=headers)
    print(f"DELETE request=> status:{new_post.status}, json:{await new_post.json()}")