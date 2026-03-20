import pytest
from playwright.sync_api import Page, expect
import re
base="https://meine-minigolf-app.calmmoss-80fcb171.germanywestcentral.azurecontainerapps.io"
base="http://localhost:8000"

@pytest.fixture(scope="session", autouse=True)
def setup():
    create_image_dir()
    yield
image_dir="test_images/start_new_game"
def create_image_dir():
    import os
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
def test_start_game(page: Page, setup):
    # Gehe zur Base-URL (aus pytest.ini)
    page.goto(base)
    page.locator("#course-name").fill("Fancy Test Course")
    # Prüfe den Titel der Seite (Passe den Text an deine App an)
    #page.screenshot({ "path": '01_course_name.png' })
    page.screenshot(path=f'{image_dir}/01_course_name.png')
    #select = page.locator("#player-count")
    players = page.get_by_label("How many players?")
    players.select_option("3 Players")
    page.screenshot(path=f'{image_dir}/02_player_count.png')
    page.get_by_role("button", name="Next").click()
    page.screenshot(path=f'{image_dir}/03_after_click_next.png')
    
    area = page.locator("#game-area")
    expect(area).to_contain_text("Enter Player Names")
    expect(area).to_contain_text("Course: Fancy Test Course")
    
    player1 = page.get_by_label("Player 1:")
    player1.fill("Morpheus")
    player2 = page.get_by_label("Player 2:")
    player2.fill("Trinity")
    player3 = page.get_by_label("Player 3:")
    player3.fill("Agent Smith")
    page.screenshot(path=f'{image_dir}/04_entered_names.png')
    page.get_by_role("button", name="Create Game").click()
    page.screenshot(path=f'{image_dir}/05_after_click_create_game.png')
    #holes = page.get_by_label("Number of Holes:")
    holes = page.locator("#holes")
    holes.select_option("18 Holes")
    page.screenshot(path=f'{image_dir}/06_after_choose_number_of_holes.png')
    page.get_by_role("button", name="Start Game").click()
    area = page.locator("#game-area")
    expect(area).to_contain_text("Hole 1 of 18")
    page.screenshot(path=f'{image_dir}/07_game_is_started.png')


