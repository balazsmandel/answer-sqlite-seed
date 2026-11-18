# Starting state: an Apache Answer site on SQLite with content

A company Q&A site running [Apache Answer](https://github.com/apache/answer) 2.0.3 (the official image, built from commit `6744295`)
with the default SQLite database, filled through the application's own API with made-up users, questions, answers,
comments, votes, edits, site settings and API keys. All people and addresses are invented.

## Set up

Needs Docker, curl and Python 3.

```sh
./setup.sh
```

It creates `~/answer` (compose file and data directory), starts the site on port 9080 and runs `seed.py` against it.
The accounts it created, their tokens and the API keys are written to `~/answer/accounts.json`.
`seed.py` uses a fixed random seed, so the content is the same on every run.
