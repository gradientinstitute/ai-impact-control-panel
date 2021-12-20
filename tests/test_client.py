'''Tests for the console client.'''
import pytest
import numpy as np
import requests
from python_client import eliciter_client


def test_server_on():
    # turn the server on


    # status: ok
    assert 0==0

def test_request_response():
    sc_url = 'http://localhost:3000/scenarios'
    sc_response = requests.get(sc_url)
    assert sc_response.ok

    al_url = 'http://localhost:3000/algorithms'
    al_response = requests.get(al_url)
    assert al_response.ok

def test_scenarios():
    assert 0==0

def test_eliciters():
    assert 0==0

def test(mocker, scenario, elic):

    fake_resp = mocker.Mock()
    fake_resp.json = mocker.Mock(return_value = scenario)
    
    assert 0==0

# human

# server

# http get . http put
# push request 
# Request . put

# mocking: fake a server

# poetry add pytest mock 
# poetry add --dev pytest-mock

# call -> server  
# response <- server
# human

# spin up the server (using testing suite) and mock the user input

# 
