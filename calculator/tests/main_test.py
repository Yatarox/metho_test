import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_add():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/add?a=2&b=3")
    assert response.status_code == 200
    assert response.json()["result"] == 5


@pytest.mark.asyncio
async def test_sub():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/sub?a=5&b=3")
    assert response.status_code == 200
    assert response.json()["result"] == 2


@pytest.mark.asyncio
async def test_mul():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/mul?a=4&b=3")
    assert response.status_code == 200
    assert response.json()["result"] == 12


@pytest.mark.asyncio
async def test_div():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/div?a=10&b=2")
    assert response.status_code == 200
    assert response.json()["result"] == 5


@pytest.mark.asyncio
async def test_div_by_zero():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/div?a=10&b=0")
    assert response.status_code == 400
    assert response.json()["detail"] == "Division by zero"


@pytest.mark.asyncio
async def test_metrics_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/metrics")
    assert response.status_code == 200
    assert "api_requests_total" in response.text