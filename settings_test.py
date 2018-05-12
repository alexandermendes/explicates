SERVER_NAME = 'localhost'
PREFERRED_URL_SCHEME = 'http'
PORT = 3001
SQLALCHEMY_DATABASE_TEST_URI = 'postgresql://rtester:rtester@localhost/explicates_test'
GENERATOR = 'http://example.org/client1'
ANNOTATIONS_PER_PAGE = 10
FLASK_PROFILER = {
  "enabled": True,
  "storage": {
      "engine": "sqlite"
  },
  "endpointRoot": "services/stats/profiler",
  "basicAuth":{
      "enabled": True,
      "username": "admin",
      "password": "admin"
  }
}
