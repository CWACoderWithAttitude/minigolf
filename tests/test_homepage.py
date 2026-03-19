import pytest
from playwright.sync_api import Page, expect
import re
base="https://meine-minigolf-app.calmmoss-80fcb171.germanywestcentral.azurecontainerapps.io"
def test_homepage_title(page: Page):
    # Gehe zur Base-URL (aus pytest.ini)
    page.goto(base)
    
    # Prüfe den Titel der Seite (Passe den Text an deine App an)
    expect(page).to_have_title("Minigolf Game") 

def test_navigation_to_scores(page: Page):
    page.goto(base)
    
    # Beispiel: Klick auf einen Button "Punktestand"
    # Ersetze ".btn-scores" durch einen echten Selektor deiner App
    scores_link = page.get_by_role("link", name="Punktestand")
    
    if scores_link.is_visible():
        scores_link.click()
        expect(page).to_have_url(re.compile(r".*/scores"))
