Feature: Health Check
  Verify that the API is running and healthy.

  Scenario: API returns healthy status
    When I send a GET request to Healthcheck endpoint
    Then I check that the http response code is "200" and the body matches the json at file "health_ok" at folder "healthcheck"
