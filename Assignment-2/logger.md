# Logger
[Back to Assignment 2](./Assignment-2.md)

---

We want to log a bunch of stuff. When receiving a request, we will store some basic data:

- datetime
- username
- endpoint
- tokens consumed

This should be stored in a data structure in Python. E.g., list or dict.
On a log request, if the list has $n$ values, it should be appended to a CSV log file in a/the Docker volume.
That way, we won't do file writing too often, as this is inefficient and slow.
The file should be named something which includes the current date.

Each new date, we make a new file. If the file does not exist, add the headers at the top of the file.

Example of CSV structure
```csv
time,username,endpoint,tokens
<time>,paul,"GET /v1.2/athlete/104"
```


## Log retention
Files with logs older than $n$ days should be deleted.
This action can be triggered on new-day logging.
We should thus only have upto $n$ log files in the log folder.
This should be able to override using an endpoint.


## Endpoints

### Add log value
`POST /log`

```JSON
{
    "username": <string>,
    ...  // Required data fields for logging
}
```

### Read retention days ($n$)
`GET /retention`

```JSON
{
    "n": <int>
}
```

### Update retentaion days ($n$)
`POST /retention`

```JSON
{
    "n": <int>
}
```
