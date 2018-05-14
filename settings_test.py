SERVER_NAME = 'localhost'
PORT = 3001
DEBUG=True
SQLALCHEMY_DATABASE_TEST_URI = 'postgresql://rtester:rtester@localhost/explicates_test'
GENERATOR = 'http://example.org/client1'
ANNOTATIONS_PER_PAGE = 3
FLASK_PROFILER = {
  "enabled": True,
  "storage": {
      "engine": "sqlite"
  },
  "endpointRoot": "server/profiler",
  "basicAuth":{
      "enabled": True,
      "username": "admin",
      "password": "admin"
  }
}
