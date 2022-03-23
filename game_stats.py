class GameStats:
    """Track statistics for Alien Invasion."""
    
    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()
        
        # Start Alien Invasion in an inactive state.
        self.game_active = False
        self.difficulty_chosen = False
        
        # High scores should never be reset.
        self.high_score = 0
    
    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
        
    def save_high_score(self):
        """Saves high score to a seperate text file."""
        with open('all_time_high_score.txt', 'w') as file_object:
            file_object.write(str(self.high_score))