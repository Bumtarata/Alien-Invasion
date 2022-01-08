import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    
    def __init__(self):
        """Initialize the game and create game resources."""
        pygame.init()
        self.settings = Settings()
        
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        
        # Create an instance to store game statistics and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        
        self._create_fleet()
        
        # Make the Play button.
        self.play_button = Button(self, "Play")
        
        # Make difficulty levels buttons.
        self.diff_buttons = [
            Button(self, "Easy"),
            Button(self, "Normal"),
            Button(self, "Hard")
        ]
        self.diff_buttons[0].rect.x = (self.settings.screen_width//2)-400
        self.diff_buttons[2].rect.x = (self.settings.screen_width//2)+200
        for button in self.diff_buttons:
            button.rect.y += 150
            button._center_msg()
            
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_screen()
                self._check_collisions()
            else:
                self._update_screen()
    
    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_buttons(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
                
    def _check_buttons(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        play_button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        easy_button_clicked = self.diff_buttons[0].rect.collidepoint(mouse_pos)
        normal_button_clicked = self.diff_buttons[1].rect.collidepoint(mouse_pos)
        hard_button_clicked = self.diff_buttons[2].rect.collidepoint(mouse_pos)
        
        if easy_button_clicked and not self.stats.game_active:
            self._choose_easy_diff()
        elif normal_button_clicked and not self.stats.game_active:
            self._choose_normal_diff()
        elif hard_button_clicked and not self.stats.game_active:
            self._choose_hard_diff()
        
        if play_button_clicked and not self.stats.difficulty_chosen and not self.stats.game_active:
            self._choose_normal_diff()
        elif play_button_clicked and self.stats.difficulty_chosen and not self.stats.game_active:
            self._start_game()
            
    def _choose_easy_diff(self):
        """Sets difficulty setting to easy."""
        self.settings.initialize_dynamic_settings()
        self.settings.alien_speed = self.settings.alien_speed - 0.25
        self.diff_buttons[0].clicked = True
        self.diff_buttons[1].clicked = False
        self.diff_buttons[2].clicked = False
        self.stats.difficulty_chosen = True
        
    def _choose_normal_diff(self):
        """Sets difficulty setting to normal."""
        self.settings.initialize_dynamic_settings()
        self.diff_buttons[0].clicked = False
        self.diff_buttons[1].clicked = True
        self.diff_buttons[2].clicked = False
        self.stats.difficulty_chosen = True
        
    def _choose_hard_diff(self):
        """Sets difficulty setting to hard."""
        self.settings.initialize_dynamic_settings()
        self.settings.alien_speed = self.settings.alien_speed + 0.25
        self.diff_buttons[0].clicked = False
        self.diff_buttons[1].clicked = False
        self.diff_buttons[2].clicked = True
        self.stats.difficulty_chosen = True
    
    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p:
            self.settings.alien_speed = 10
        elif event.key == pygame.K_o:
            self.settings.bullet_width = 400
            
    def _check_keyup_events(self, event):
        """Responds to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
            
    def _start_game(self):
        """Starts a new game."""
        # Reset the game statistics.
        self.stats.reset_stats()
        self.sb.prep_score()
        self.stats.game_active = True
            
        # Get rid of any remaining aliens and bullets.
        self.aliens.empty()
        self.bullets.empty()
            
        # Create a new fleet and center the ship.
        self._create_fleet()
        self.ship.center_ship()
        
        # Hide the mouse cursor.
        pygame.mouse.set_visible(False)
        
        # Unclick all difficulty level buttons.
        for button in self.diff_buttons:
            button.clicked = False
            
    def _fire_bullet(self):
        """Create bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet position.
        self.bullets.update()
        # Get rid of bullets that have disappeared.
        for bullet in self.bullets:
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()
            
    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullet and alien that have collided.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
            
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
            
        if not self.aliens:
        # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
        
    def _update_aliens(self):
        """Check if the fleet is at an edge,
        then update the position of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()
        
    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left - 1 > 0:
            # Decrement ships_left.
            self.stats.ships_left -= 1
            
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # Pause
            sleep(1)
        else:
            self.stats.game_active = False
            self.stats.difficulty_chosen = False
            pygame.mouse.set_visible(True)
        
    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break
    
    def _check_collisions(self):
        """Checks for alen-ship and alien-bottom of the screen collisions."""
        # Checks for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()
                
    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (1.5 * alien_width)
        
        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) -
                            ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        # Create the full fleet of aliens.
        for row_number in range(number_rows - 1):
            for alien_number in range(int(number_aliens_x)):
                self._create_alien(alien_number, row_number)
    
    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 1.5 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 1.5 * alien.rect.height * row_number
        self.aliens.add(alien)
    
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
                
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    
    def _update_screen(self):
        """Update images on the screen and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        
        # Draw the score information.
        self.sb.show_score()
        
        # Draw the play and difficulty buttons if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
            
            for button in self.diff_buttons:
                button.draw_button()
        
        # Make the most recently drawn screen visible.
        pygame.display.flip()
        

if __name__ == "__main__":
    # Make a game instance and run the game.
    ai = AlienInvasion()
    ai.run_game()