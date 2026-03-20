import pytest
from playwright.sync_api import Page, expect
import re
base="https://meine-minigolf-app.calmmoss-80fcb171.germanywestcentral.azurecontainerapps.io"
base="http://localhost:8000"

@pytest.fixture(scope="session", autouse=True)
def setup():
    create_image_dir()
    yield
image_dir="test_images/play_hole1"
def create_image_dir():
    import os
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
def test_start_game(page: Page, setup):
    # Gehe zur Base-URL (aus pytest.ini)
    page.goto(base)
    page.locator("#course-name").fill("Fancy Test Course")
    players = page.get_by_label("How many players?")
    players.select_option("3 Players")
    page.get_by_role("button", name="Next").click()
    
    area = page.locator("#game-area")
    expect(area).to_contain_text("Enter Player Names")
    expect(area).to_contain_text("Course: Fancy Test Course")
    
    player1 = page.get_by_label("Player 1:")
    player1.fill("Morpheus")
    player2 = page.get_by_label("Player 2:")
    player2.fill("Trinity")
    player3 = page.get_by_label("Player 3:")
    player3.fill("Agent Smith")
    page.get_by_role("button", name="Create Game").click()
    #holes = page.get_by_label("Number of Holes:")
    holes = page.locator("#holes")
    holes.select_option("18 Holes")
    page.get_by_role("button", name="Start Game").click()
    area = page.locator("#game-area")
    expect(area).to_contain_text("Hole 1 of 18")
    page.screenshot(path=f'{image_dir}/01_start_recording.png', full_page=True)
    
    page.get_by_label("Trinity:").fill("3")
    page.get_by_label("Morpheus:").fill("2")
    page.get_by_label("Agent Smith:").fill("4")
    page.screenshot(path=f'{image_dir}/02_recorded_all_scores.png', full_page  = True)
    page.get_by_role("button", name="Record Hole").click()
    expect(area).to_contain_text("Hole 2 of 18")
    page.screenshot(path=f'{image_dir}/03_after_first_hole.png', full_page  = True)

