# Rate limiter
[Back to Assignment 2](./Assignment-2.md)

---

This node keeps track of how many requests each user have performed in the last $n$ seconds (hereby 10 seconds). When the number of requests a user performes surpasses 10 the last 10 seconds, slow them down.

It should have the following endpoints:

### Add a new request
`POST /<user-id>`
```JSON
{
    "username": <string>
}
```

### Retrieve number of requests the last 10 seconds
`GET /<user-id>`
```JSON
{
    "requests": <int>,
    "delay": <float>
}
```

When the last 10 seconds have 10 or more requests, it should return a number of seconds of delay before returning the results. E.g.,

```python
delay: float = ...  # API call
time.sleep(delay)  # Sleep for `delay` seconds
return whatever
```

The Rate limiter should calculate the amount of seconds based on the following function.

$$ f(r) = \frac{r}{10} $$

where $r$ is the number of request _over the allowed limit (10)_ the last 10 seconds. So when passing 10 requests the last 10 seconds, add a tenth of a second per these requests.

Example pseudo-ish code:

```python
DATA = {
    ...  # user_id: [list-of-datetimes]
} 

# POST request
DATA[<user-id>].append(<datetime>)  # Maybe clear >10 seconds old requests?

# GET request
requests = len(DATA[<user-id>])  # Maybe clear >10 second old requests?
delay = 0
if requests > 10:
    r = requests - 10  # Excess requests
    delay = r/10
return {"requests": requests, "delay": delay}
```
