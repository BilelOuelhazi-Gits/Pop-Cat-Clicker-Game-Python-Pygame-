import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions (assuming a phone screen ratio)
WIDTH, HEIGHT = 480, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pop Cat Game")

# Load images
not_clicked = pygame.image.load("assets/animations/not_clicked.png")
clicked = pygame.image.load("assets/animations/clicked.png")

# Resize images to fit the screen
not_clicked = pygame.transform.scale(not_clicked, (WIDTH - 40, WIDTH - 40))  # Keep it proportional to screen size
clicked = pygame.transform.scale(clicked, (WIDTH - 40, WIDTH - 40))

# Load sounds
sound_paths = [
    "assets/sounds/sound1.mp3",
    "assets/sounds/sound2.mp3",
    "assets/sounds/sound3.mp3",
]
sounds = [pygame.mixer.Sound(path) for path in sound_paths]

# Game variables
image_rect = not_clicked.get_rect(center=(WIDTH // 2, HEIGHT // 3))
current_image = not_clicked
click_count = 0
points_per_click = 1
auto_clicker_rate = 0  # Points per second
abilities = [
    {"name": "Pts Mult", "cost": 50, "type": "multiplier", "value": 1},
    {"name": "Auto Click", "cost": 100, "type": "auto_clicker", "value": 1},
    {"name": "Pts Mult", "cost": 150, "type": "multiplier", "value": 2},
    {"name": "Auto Click", "cost": 200, "type": "auto_clicker", "value": 2},
    {"name": "Pts Mult", "cost": 250, "type": "multiplier", "value": 3},
    {"name": "Auto Click", "cost": 300, "type": "auto_clicker", "value": 3},
    {"name": "Pts Mult", "cost": 350, "type": "multiplier", "value": 4},
    {"name": "Auto Click", "cost": 400, "type": "auto_clicker", "value": 4},
    {"name": "Pts Mult", "cost": 450, "type": "multiplier", "value": 5},
]
font = pygame.font.Font(None, 30)  # Reduced font size for shorter ability names
large_font = pygame.font.Font(None, 40)
last_sound_index = -1
last_auto_click_time = 0
dragging = False
drag_offset = 0
scroll_y = 0
max_abilities = 9  # Limit the number of abilities in the shop (3x3 grid)
last_click_time = 0
click_cooldown = 100  # 100ms cooldown between clicks
last_n_sounds = []  # Store recently played sounds


# Helper function to generate new abilities
def generate_new_ability():
    cost = random.randint(200, 500)
    ability_type = random.choice(["multiplier", "auto_clicker"])
    value = random.randint(1, 3) if ability_type == "multiplier" else random.randint(1, 5)
    name = f"{'Pts Mult' if ability_type == 'multiplier' else 'Auto Click'} Lv{value}"
    return {"name": name, "cost": cost, "type": ability_type, "value": value}


# Draw a button with rounded corners and a soft shadow, name at the top and price at the bottom
def draw_rounded_button(screen, rect, color, border_color, name, price, font, padding=10):
    pygame.draw.rect(screen, border_color, rect, border_radius=15)
    pygame.draw.rect(screen, color, rect.inflate(-padding, -padding), border_radius=15)

    # Render the ability name and price
    name_surface = font.render(name, True, (0, 0, 0))
    price_surface = font.render(f"{price} pts", True, (0, 0, 0))

    # Calculate the positions for the name and price text
    name_rect = name_surface.get_rect(center=(rect.centerx, rect.top + 20))
    price_rect = price_surface.get_rect(center=(rect.centerx, rect.bottom - 20))

    # Blit the text
    screen.blit(name_surface, name_rect)
    screen.blit(price_surface, price_rect)


# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill((255, 240, 240))  # Soft pink pastel background

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if image_rect.collidepoint(event.pos):
                # Cooldown between clicks
                if pygame.time.get_ticks() - last_click_time > click_cooldown:
                    current_image = clicked
                    click_count += points_per_click
                    # Play a random sound (not the same as the last one)
                    next_sound_index = random.choice(
                        [i for i in range(len(sounds)) if i not in last_n_sounds]
                    )
                    sounds[next_sound_index].play()

                    last_n_sounds.append(next_sound_index)
                    if len(last_n_sounds) > 2:
                        last_n_sounds.pop(0)

                    last_click_time = pygame.time.get_ticks()

            # Check if clicking on shop abilities
            for idx, ability in enumerate(abilities[:max_abilities]):
                row = idx // 3  # Determine the row (0, 1, 2)
                col = idx % 3  # Determine the column (0, 1, 2)
                ability_rect = pygame.Rect(20 + col * (WIDTH // 3 - 10 + 10), 550 + row * 80 - scroll_y, WIDTH // 3 - 20, 60)
                if ability_rect.collidepoint(event.pos):
                    if click_count >= ability["cost"]:
                        click_count -= ability["cost"]
                        if ability["type"] == "multiplier":
                            points_per_click += ability["value"]
                        elif ability["type"] == "auto_clicker":
                            auto_clicker_rate += ability["value"]
                        ability["cost"] = int(ability["cost"] * 1.5)  # Increase cost
                        # Generate a new ability when purchased
                        if random.random() > 0.5:  # 50% chance
                            abilities.append(generate_new_ability())

        if event.type == pygame.MOUSEMOTION:
            if dragging:
                # Invert the scroll direction by subtracting the difference instead of adding
                scroll_y = drag_offset - event.pos[1]

        if event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            current_image = not_clicked

    # Scroll limits
    scroll_y = max(0, min(scroll_y, (max_abilities // 3) * 80 - (HEIGHT - 100)))

    # Draw current image
    screen.blit(current_image, image_rect)

    # Display score in the center at the top with soft, rounded corners for the text box
    score_text = large_font.render(f"Score: {click_count}", True, (0, 0, 0))
    score_rect = pygame.Rect(WIDTH // 2 - score_text.get_width() // 2 - 20, 10,
                             score_text.get_width() + 40, score_text.get_height() + 20)
    pygame.draw.rect(screen, (255, 195, 197), score_rect, border_radius=15)  # Rounded background
    pygame.draw.rect(screen, (172, 124, 120), score_rect, 5, border_radius=15)  # Border
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    # Display shop title further down with a cute color
    shop_title = large_font.render("  Shop", True, (172, 124, 120))  # #ac7c78
    screen.blit(shop_title, (20, 500))  # Move the title further down

    # Draw a border for the shop section
    shop_rect = pygame.Rect(20, 480, WIDTH - 40, HEIGHT - 480)  # Area for the shop, including title and buttons
    pygame.draw.rect(screen, (172, 124, 120), shop_rect, 5, border_radius=15)  # Border for the entire shop area

    # Display abilities with cute rounded buttons in a 3x3 grid
    for idx, ability in enumerate(abilities[:max_abilities]):
        row = idx // 3  # Determine the row (0, 1, 2)
        col = idx % 3  # Determine the column (0, 1, 2)
        ability_rect = pygame.Rect(20 + col * (WIDTH // 3 - 10 + 10), 550 + row * 80 - scroll_y, WIDTH // 3 - 20, 60)

        # Draw ability buttons with name at the top and price at the bottom inside the button
        if ability_rect.collidepoint(pygame.mouse.get_pos()):
            draw_rounded_button(screen, ability_rect, (255, 195, 197), (172, 124, 120), ability["name"],
                                ability["cost"], font)
        else:
            draw_rounded_button(screen, ability_rect, (172, 124, 120), (255, 195, 197), ability["name"],
                                ability["cost"], font)

    # Update the display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
