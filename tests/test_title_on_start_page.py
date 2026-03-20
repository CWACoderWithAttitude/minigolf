import pytest
from playwright.sync_api import Page, expect
import re
base="https://meine-minigolf-app.calmmoss-80fcb171.germanywestcentral.azurecontainerapps.io"
base="http://localhost:8000"
def test_check_title(page: Page):
    # Gehe zur Base-URL (aus pytest.ini)
    page.goto(base)
    expect(page).to_have_title("Minigolf Game") 
    page.screenshot(path='00_window_Title_should_be_OK.png')

