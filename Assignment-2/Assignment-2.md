# Assignment 2

## Project
This assignment builds on assignment 1, but there are additions.

All services will run in Docker containers, using a Docker Compose to launch it. Containers should at least include:

| Component               | Description                                  | Link                                               |
| ----------------------- | -------------------------------------------- | -------------------------------------------------- |
| Main API                | This is mostly the API from assignment 1     | [Assignment-1.md](../Assignment-1/Assignment-1.md) |
| Token shop              | This performs the token buying               | [token-shop.md](./token-shop.md)                   |
| Database                | About our database system(s)                 | [database.md](./database.md)                       |
| Cache                   | Caching requests                             | [cache.md](./cache.md)                             |
| Rate limiter (per user) | Limiting users when they request too quickly | [rate-limiter.md](./rate-limiter.md)               |
| Logger                  | Logging request data                         | [logger.md](./logger.md)                           |

The Main API is the one from assignment 1, with whichever modifications are required. Remember that we are now at `v2`, not `v1`.

Additionally, it should include volumes for the dataset and for logs. You may have to make more containers, volumes, networks or databases for your subsystems. Do so when necessary.

You may need to add more features than specified. You may also need to modify some of the examples or instructions, e.g., adding more data to an API request than suggested/specified.


## Report and more
Make sure to read the README file in the root of the repo, as it contains information about the report and more.
