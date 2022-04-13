# run-mooc-jutut

Docker container for running [MOOC-Jutut](https://github.com/apluslms/mooc-jutut).
This is intended for local development and testing.

# Usage

MOOC-jutut is installed in `/srv/jutut`.
You can mount development version of the source code to `/src/jutut`.
The container will then copy it to `/srv/jutut` and compile
the translation file (django.mo). If you mount directly to
`/srv/jutut`, you need to manually compile the translation file beforehand,
but on the other hand, Django can reload the code and restart the server
without restarting the whole container when you edit the source code files.

You can mount development version of the MOOC-Jutut source code on top of that, if you wish.

Location `/data` is a volume and contains the database and secret key.
It is world writable, so you can run this container as normal user.

Partial example of `docker-compose.yml` (volumes are optional of course):

```yaml
services:
  jutut:
    image: apluslms/run-mooc-jutut
    volumes:
    # named persistent volume (until removed)
    # - data:/data
    # mount development version to /src/jutut
    # - /home/user/mooc-jutut/:/src/jutut/:ro
    # or to /srv/jutut
    # - /home/user/mooc-jutut/:/srv/jutut/:ro
    ports:
      - "8082:8082"
volumes:
  data:
```
