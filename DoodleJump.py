import pygame            # Import Pygame library for game development
import random            # Import random module for generating random values
import Platform          # Import custom Platform module (user-defined)
import neuralnet as nn   # Import user-defined neural network module as nn
import Player            # Import custom Player module
import ga                # Import genetic algorithm module
import time              # Import time module for tracking elapsed time


W = 600                  # Screen width
H = 800                  # Screen height
TOTAL = 20               # Number of players (agents)


class DoodleJump():      # Define main game class
    def __init__(self):  # Constructor to initialize game state
        self.screen = pygame.display.set_mode((W, H))    # Create game window
        pygame.font.init()                               # Initialize font module
        self.score = 0                                   # Game score
        self.font = pygame.font.SysFont("Arial", 25)     # Font for text display

        # Load and scale platform and item assets
        self.green = pygame.transform.scale(pygame.image.load("assets/green.png"), (80,25)).convert_alpha()
        self.blue = pygame.transform.scale(pygame.image.load("assets/blue.png"), (80,25)).convert_alpha()
        self.red = pygame.transform.scale(pygame.image.load("assets/red.png"), (80,25)).convert_alpha()
        self.red_1 = pygame.transform.scale(pygame.image.load("assets/redBroken.png"), (80,40)).convert_alpha()
        self.spring = pygame.transform.scale(pygame.image.load("assets/spring.png"), (25,25)).convert_alpha()
        self.spring_1 = pygame.transform.scale(pygame.image.load("assets/spring_1.png"), (25,25)).convert_alpha()

        self.gravity = 0                  # Gravity value
        self.camera = 0                   # Camera position
        self.platforms = []              # List of platforms
        self.generation = 1              # Current generation number
        self.time = time.time()          # Time tracking for stuck detection
        self.startY = -100               # Y-position to start generating platforms

    def playerUpdate(self, player):  # Update camera position relative to player
        if (player.y - self.camera <= 200):
            self.camera -= 8             # Move camera up as player jumps

    def drawPlayer(self, player):   # Draw the player based on direction and jumping state
        if (player.direction == 0):  # Facing right
            if (player.jump > 0):
                self.screen.blit(player.playerRight_1, (player.x, player.y - self.camera))
            else:
                self.screen.blit(player.playerRight, (player.x, player.y - self.camera))
        else:  # Facing left
            if (player.jump):
                self.screen.blit(player.playerLeft_1, (player.x, player.y - self.camera))
            else:
                self.screen.blit(player.playerLeft, (player.x, player.y - self.camera))

    def updateplatforms(self, player):  # Handle collisions between player and platforms
        for p in self.platforms:
            rect = pygame.Rect(p.x + 10, p.y, p.green.get_width() - 25, p.green.get_height() - 20)
            playerCollider = pygame.Rect(player.x, player.y, player.playerRight.get_width() - 10, player.playerRight.get_height())
            
            if (rect.colliderect(playerCollider) and player.gravity > 0 and player.y < (p.y - self.camera)):
                if (p.kind != 2):       # If platform is not red (fragile)
                    player.jump = 20    # Bounce up
                    player.gravity = 0
                else:
                    p.broken = True    # Break fragile red platform

    def drawplatforms(self):  # Draw all platforms and update moving ones
        for p in self.platforms:
            y = p.y - self.camera

            if (y > H):                 # If platform is off-screen
                self.generateplatforms(False)  # Generate new one
                self.platforms.pop(0)          # Remove old one
                self.score += 10               # Increase score
                self.time = time.time()        # Reset time

            if (p.kind == 1):          # Move blue platforms
                p.blueMovement(self.score)

            # Draw platform based on kind
            if (p.kind == 0):
                self.screen.blit(p.green, (p.x, y))
            elif (p.kind == 1):
                self.screen.blit(p.blue, (p.x, y))
            elif (p.kind == 2):
                if not p.broken:
                    self.screen.blit(p.red, (p.x, y))
                else:
                    self.screen.blit(p.red_1, (p.x, y))

    def generateplatforms(self, initial):  # Generate initial or new platform
        y = 900
        start = -100
        if (initial == True):
            self.startY = -100
            while (y > -70):
                p = Platform.Platform()
                p.getKind(self.score)
                p.y = y
                p.startY = start
                self.platforms.append(p)
                y -= 30
                start += 30
                self.startY = start
        else:
            p = Platform.Platform()
            if (self.score <= 2500):
                difficulty = 50
            elif (self.score < 4000):
                difficulty = 60
            else:
                difficulty = 70
            p.y = self.platforms[-1].y - difficulty
            self.startY += difficulty
            p.startY = self.startY
            p.getKind(self.score)
            self.platforms.append(p)

    def update(self):  # Update score and generation display
        self.drawplatforms()
        self.screen.blit(self.font.render("Score: " + str(self.score), -1, (0, 0, 0)), (25, 25))
        self.screen.blit(self.font.render("Generation: " + str(self.generation), -1, (0, 0, 0)), (25, 60))

    def run(self):  # Main game loop
        background_image = pygame.image.load('assets/background.png')  # Load background
        clock = pygame.time.Clock()            # Create clock to limit FPS
        TOTAL = 500                            # Number of AI agents
        savedDoodler = []                      # Store dead doodlers
        GA = ga.GeneticAlgorithm()             # Create GeneticAlgorithm object
        doodler = GA.populate(TOTAL, None)     # Generate initial doodlers

        run = True
        self.generateplatforms(True)           # Generate initial platforms
        highestScore = 0

        while run:
            self.screen.fill((255,255,255))    # Clear screen
            self.screen.blit(background_image, [0, 0])  # Draw background
            clock.tick(60)                     # Limit to 60 FPS

            for event in pygame.event.get():   # Handle quit event
                if event.type == pygame.QUIT:
                    run = False

            currentTime = time.time()
            if (currentTime - self.time > 15):  # If stuck for 15s, clear population
                self.time = time.time()
                for d in doodler:
                    d.fitness = self.score
                    d.fitnessExpo()
                doodler.clear()

            if (len(doodler) == 0):            # If all players are dead
                self.camera = 0
                self.time = time.time()
                self.score = 0
                doodler.clear()
                self.platforms.clear()
                self.generateplatforms(True)

                if (self.generation > 100 and highestScore < 4000):  # Reset if no progress
                    print("RESET")
                    self.generation = 0
                    doodler = GA.populate(TOTAL, None)
                else:
                    self.generation += 1
                    GA.nextGeneration(TOTAL, savedDoodler)
                    doodler = GA.doodler

                savedDoodler.clear()

            self.update()                      # Draw and update platforms

            for d in doodler:                  # Loop over each doodler/player
                d.fitness = self.score         # Update fitness
                d.move(d.think(self.platforms))# Move based on neural net decision
                self.drawPlayer(d)             # Draw player sprite
                self.playerUpdate(d)           # Update camera
                self.updateplatforms(d)        # Handle collisions

                if (d.y - self.camera > 800):  # If player fell off screen
                    d.fitnessExpo()
                    savedDoodler.append(d)
                    doodler.remove(d)

            if (self.score > highestScore):    # Track high score
                highestScore = self.score

            # Draw UI
            self.screen.blit(self.font.render("Count: " + str(len(doodler)), -1, (0, 0, 0)), (25, 120))
            self.screen.blit(self.font.render("High Score: " + str(highestScore), -1, (0, 0, 0)), (25, 90))

            pygame.display.update()            # Refresh screen


DoodleJump().run()  # Run the game
