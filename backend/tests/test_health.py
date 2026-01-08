def test_api_esta_rodando(client):
    response = client.get("/docs")

    assert response.status_code == 200
