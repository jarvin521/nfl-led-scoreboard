from PIL import Image, ImageFont, ImageDraw, ImageSequence
#from rgbmatrix import graphics
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
from utils import center_text
from calendar import month_abbr
from renderer.screen_config import screenConfig
from datetime import datetime, timedelta
import time as t
import debug
import re

GAMES_REFRESH_RATE = 900.0

class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.screen_config = screenConfig("64x32_config")
        self.canvas = matrix.CreateFrameCanvas()
        self.width = 64
        self.height = 64
        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_03B_.TTF", 8)

    def render(self):
        while True:
            self.starttime = t.time()
            self.data.get_current_date()
            self.__render_game()

    def __render_game(self):
        while True:
            # If we need to refresh the overview data, do that
            if self.data.needs_refresh:
                self.data.refresh_games()

            # Draw the current game
            self.__draw_game(self.data.current_game())

            # Set the refresh rate
            refresh_rate = self.data.config.scrolling_speed
            t.sleep(refresh_rate)
            endtime = t.time()
            time_delta = endtime - self.starttime
            rotate_rate = self.__rotate_rate_for_game(self.data.current_game())

            # If we're ready to rotate, let's do it
            if time_delta >= rotate_rate:
                self.starttime = t.time()
                self.data.needs_refresh = True

                if self.__should_rotate_to_next_game(self.data.current_game()):
                    game = self.data.advance_to_next_game()

                if endtime - self.data.games_refresh_time >= GAMES_REFRESH_RATE:
                    self.data.refresh_games()

                if self.data.needs_refresh:
                    self.data.refresh_games()

    def __rotate_rate_for_game(self, game):
        rotate_rate = self.data.config.rotation_rates_live
        if game['state'] == 'pre':
            rotate_rate = self.data.config.rotation_rates_pregame
        if game['state'] == 'post':
            rotate_rate = self.data.config.rotation_rates_final
        return rotate_rate

    def __should_rotate_to_next_game(self, game):
        if self.data.config.rotation_enabled == False:
            return False

        stay_on_preferred_team = self.data.config.preferred_teams and not self.data.config.rotation_preferred_team_live_enabled
        if stay_on_preferred_team == False:
            return True
        else:
            return False

        # figure this out later heh
        # showing_preferred_team = self.data.config.preferred_teams[0] in [game.awayteam, game.hometeam]
        # if showing_preferred_team and game['status']:
        #     if self.data.config.rotation_preferred_team_live_mid_inning == True and Status.is_inning_break(overview.inning_state):
        #         return True
        #     return False

        # return True

    def __draw_game(self, game):
        time = self.data.get_current_date()
        gametime = datetime.strptime(game['date'], "%Y-%m-%dT%H:%MZ")
        if time < gametime and game['state'] == 'pre':
            debug.info('Pre-Game State')
            self._draw_pregame(game)
        elif game['state'] == 'post':
            if game['stateDetail'] == 'Postponed':
                debug.info('Postponed')
                self._draw_postponed(game)
            else:
                debug.info('Final State')
                self._draw_post_game(game)
        else:
            debug.info('Live State, checking every 5s')
            self._draw_live_game(game)
        debug.info('ping render_game')

    def _draw_pregame(self, game):
            time = self.data.get_current_date()
            gamedatetime = self.data.get_gametime()
            if gamedatetime.day == time.day:
                date_text = 'TODAY'
            else:
                date_text = gamedatetime.strftime('%-m/%-d')  
            gametime = gamedatetime.strftime("%-I:%M %p")
            
            # Center the game time on screen.                
            date_pos = center_text(self.font_mini.getbbox(date_text)[2], 32)
            gametime_pos = center_text(self.font_mini.getbbox(gametime)[2], 32)
            
            # Draw the text on the Data image.
            self.draw.text((date_pos, 0), date_text, font=self.font_mini)
            self.draw.multiline_text((gametime_pos, 6), gametime, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.text((25, 15), 'VS', font=self.font)
            
            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)
            
            # TEMP Open the logo image file
            away_team_logo = Image.open('logos/{}/{}.png'.format(game['league'], game['awayteam'])).resize((16, 16), Image.BOX)
            home_team_logo = Image.open('logos/{}/{}.png'.format(game['league'], game['hometeam'])).resize((16, 16), Image.BOX)
            
            # Put the images on the canvas
            self.canvas.SetImage(away_team_logo.convert("RGB"), 2, 14)
            self.canvas.SetImage(home_team_logo.convert("RGB"), 45, 14)

            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

    def _draw_live_game(self, game):
        homescore = game['homescore']
        awayscore = game['awayscore']
        print("home: ", homescore, "away: ", awayscore)
        # Refresh the data
        quarter = str(game['quarter']) # I'm using quarter but it works as half or period or inining
        if self.data.needs_refresh:
            debug.info('Refresh game overview')
            self.data.refresh_games()
            self.data.needs_refresh = False
        if game['league'] != 'mlb':
            time_period = game['time']
            time_period_pos = center_text(self.font_mini.getbbox(time_period)[2], 32)
            self.draw.multiline_text((time_period_pos, 14), time_period, fill=(255, 255, 255), font=self.font_mini, align="center")
        if game['league'] == 'nfl' or game['league'] == 'ncaa':
            if game['possession'] == game['awayid']:
                pos = game['awayteam']
            else:
                pos = game['hometeam']
                # this is ugly but I want to replace the possession info with down info and spot info
            down = None
            spot = None
            game_info = None
            if game['down']:
                down = re.sub(r"[a-z]+", "", game['down']).replace(" ", "")
                info_pos = center_text(self.font_mini.getbbox(str(down))[2], 32)
                self.draw.multiline_text((info_pos, 19), str(down), fill=(255, 255, 255), font=self.font_mini, align="center")
            if game['spot']:
                spot = game['spot'].replace(" ", "")
                info_pos = center_text(self.font_mini.getbbox(spot)[2], 32)
                self.draw.multiline_text((info_pos, 25), spot, fill=(255, 255, 255), font=self.font_mini, align="center")
            pos_colour = (255, 255, 255)
            if game['redzone']:
                pos_colour = (255, 25, 25)
        # Set the position of the information on screen.
        homescore = '{0:d}'.format(homescore)
        awayscore = '{0:d}'.format(awayscore)
        home_score_size = self.font.getbbox(homescore)[2]
        if game['league'] == 'mlb':
            balls = f"B {game['balls']}"
            strikes = f"S {game['strikes']}"
            outs = f"O {game['outs']}" 
            self.draw.multiline_text((center_text(self.font_mini.getbbox(balls)[2], 32), 12), balls, fill=(255, 255, 255), font=self.font_mini, align="center")  
            self.draw.multiline_text((center_text(self.font_mini.getbbox(strikes)[2], 32), 18), strikes, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.multiline_text((center_text(self.font_mini.getbbox(outs)[2], 32), 24), outs, fill=(255, 255, 255), font=self.font_mini, align="center")
        elif game['league'] == 'nfl' or game['league'] == 'ncaa':
            info_pos = center_text(self.font_mini.getbbox(pos)[2], 32)
            self.draw.multiline_text((info_pos, 13), pos, fill=pos_colour, font=self.font_mini, align="center")
        else:
            print("basketball game")
        
        # score_position = center_text(self.font.getsize(score)[0], 32)
        quarter_position = center_text(self.font.getbbox(quarter)[2], 32)     
        self.draw.multiline_text((quarter_position, 0), quarter, fill=(255, 255, 255), font=self.font, align="center")
        self.draw.multiline_text((6, 19), awayscore, fill=(255, 255, 255), font=self.font, align="center")
        self.draw.multiline_text((59 - home_score_size, 19), homescore, fill=(255, 255, 255), font=self.font, align="center")
        
        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)
        
        # TEMP Open the logo image file
        away_team_logo = Image.open('logos/{}/{}.png'.format(game['league'], game['awayteam'])).resize((16, 16), Image.BOX)
        home_team_logo = Image.open('logos/{}/{}.png'.format(game['league'], game['hometeam'])).resize((16, 16), Image.BOX)
        
        # Put the images on the canvas
        self.canvas.SetImage(away_team_logo.convert("RGB"), 2, 0)
        self.canvas.SetImage(home_team_logo.convert("RGB"), 45, 0)
        
        # Load the canvas on screen.
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        # Refresh the Data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        # Check if the game is over
        if game['state'] == 'post':
            debug.info('GAME OVER')
        # Save the scores.
        self.data.needs_refresh = True

    def _draw_postponed(self, game):
              
        # # Set the position of the information on screen. 
        self.draw.multiline_text((25, 2), "PPD", fill=(255, 255, 255), font=self.font_mini, align="center")

        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)

        # TEMP Open the logo image file
        away_team_logo = Image.open('logos/{}/{}.png'.format(game['league'], game['awayteam'])).resize((16, 16), Image.BOX)
        home_team_logo = Image.open('logos/{}/{}.png'.format(game['league'], game['hometeam'])).resize((16, 16), Image.BOX)
        rain = Image.open('logos/rain.bmp').resize((16, 16), Image.BOX)
        
        # Put the images on the canvas
        self.canvas.SetImage(rain.convert("RGB"), 24, 12)
        self.canvas.SetImage(away_team_logo.convert("RGB"), 2, 7)
        self.canvas.SetImage(home_team_logo.convert("RGB"), 45, 7)
       
        # Load the canvas on screen.
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

        # Refresh the Data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

    def _draw_post_game(self, game):
        self.draw.multiline_text((21, 0), "FINAL", fill=(255, 255, 255), font=self.font_mini,align="center")
        score = '{}-{}'.format(game['awayscore'], game['homescore'])
        # Set the position of the information on screen.
        score_position = center_text(self.font.getbbox(score)[2], 32)
        # Draw the text on the Data image.
        self.draw.multiline_text((score_position, 19), score, fill=(255, 255, 255), font=self.font, align="center")
        
        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)

        # TEMP Open the logo image file
        away_team_logo = Image.open('logos/{}/{}.png'.format(game['league'], game['awayteam'])).resize((16, 16), Image.BOX)
        home_team_logo = Image.open('logos/{}/{}.png'.format(game['league'], game['hometeam'])).resize((16, 16), Image.BOX)
        
        # Put the images on the canvas
        self.canvas.SetImage(away_team_logo.convert("RGB"), 2, 2)
        self.canvas.SetImage(home_team_logo.convert("RGB"), 45, 2)

        # Load the canvas on screen.
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        # Refresh the Data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
