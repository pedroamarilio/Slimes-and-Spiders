import pygame
from PPlay.sprite import Sprite


class SceneMenu:
    """Simple main menu scene.

    Usage:
        menu = SceneMenu(janela)
        action = menu.run()  # returns 'play' or 'exit'
    """

    def __init__(self, janela):
        self.janela = janela
        self.mouse = janela.get_mouse()
        self.keyboard = janela.get_keyboard()

        # Load assets (fall back gracefully if missing)
        try:
            self.bg = Sprite('assets/sprites/menubackground.png', 1)
        except Exception:
            self.bg = None
        try:
            self.logo = Sprite('assets/sprites/logo.png', 1)
        except Exception:
            self.logo = None

        # Buttons and their selected variants
        try:
            self.play = Sprite('assets/sprites/playbutton.png', 1)
        except Exception:
            self.play = None
        try:
            self.exit = Sprite('assets/sprites/exitbutton.png', 1)
        except Exception:
            self.exit = None
        try:
            self.play_sel = Sprite('assets/sprites/selectedplay.png', 1)
        except Exception:
            self.play_sel = None
        try:
            self.exit_sel = Sprite('assets/sprites/selectedexit.png', 1)
        except Exception:
            self.exit_sel = None

        # layout
        w = getattr(self.janela, 'width', 1366)
        h = getattr(self.janela, 'height', 768)

        # logo at top center
        if self.logo:
            lx = int((w - self.logo.width) / 2)
            self.logo.set_position(lx, 48)

        # buttons centered below logo (moved slightly down)
        btn_y = 320
        if self.play:
            bx = int((w - self.play.width) / 2)
            self.play.set_position(bx, btn_y)
            if self.play_sel:
                self.play_sel.set_position(bx, btn_y)

        if self.exit:
            ex = int((w - (self.exit.width if self.exit else 0)) / 2)
            self.exit.set_position(ex, btn_y + (self.play.height if self.play else 80) + 20)
            if self.exit_sel:
                self.exit_sel.set_position(ex, btn_y + (self.play.height if self.play else 80) + 20)

    def run(self):
        clock = pygame.time.Clock()

        while True:
            # draw background + logo + buttons
            try:
                if self.bg:
                    self.bg.draw()
            except Exception:
                pass

            if self.logo:
                try:
                    self.logo.draw()
                except Exception:
                    pass

            # draw normal buttons by default
            if self.play:
                try:
                    self.play.draw()
                except Exception:
                    pass
            if self.exit:
                try:
                    self.exit.draw()
                except Exception:
                    pass

            # present frame
            try:
                self.janela.update()
            except Exception:
                pass

            # input handling
            if self.mouse.is_button_pressed(1):
                # left-click; check which button was clicked
                try:
                    if self.play and self.mouse.is_over_object(self.play):
                        # show selected visual briefly
                        if self.play_sel:
                            try:
                                self.play_sel.draw()
                                self.janela.update()
                            except Exception:
                                pass
                        pygame.time.delay(140)
                        return 'play'
                    if self.exit and self.mouse.is_over_object(self.exit):
                        if self.exit_sel:
                            try:
                                self.exit_sel.draw()
                                self.janela.update()
                            except Exception:
                                pass
                        pygame.time.delay(140)
                        return 'exit'
                except Exception:
                    pass

            # keyboard shortcuts
            try:
                if self.keyboard.key_pressed('ENTER') or self.keyboard.key_pressed('RETURN'):
                    return 'play'
                if self.keyboard.key_pressed('ESC'):
                    return 'exit'
            except Exception:
                pass

            clock.tick(60)
