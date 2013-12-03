import realms

c = realms.app.test_client()
print c.get('/wiki/_create')
print c.get('/wiki/_create/blah')