# drongo-nest [![Build Status](https://api.travis-ci.org/drongo-framework/drongo-nest.svg?branch=master)](https://travis-ci.org/drongo-framework/drongo-nest) [![Coverage](https://codecov.io/github/drongo-framework/drongo-nest/coverage.svg?branch=master)](https://codecov.io/github/drongo-framework/drongo-nest/)
High performance server for drongo.

## Getting Started
```
from drongo import Drongo
from nest import Nest


app = Drongo()  # Drongo app
nest = Nest(app=app, auto_reload=True)
try:
    nest.run()
except KeyboardInterrupt:
    print('Shutting down')
finally:
    nest.shutdown()
```
