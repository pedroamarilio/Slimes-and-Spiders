from PPlay.window import *
BTN_H = 64
BTN_W = 64
GAP = 4
global menu_atual

class Button:
    def __init__(self, label, icon, action, hotkey=None):
        self.label = label
        self.icon = icon         # Surface do sprite recortado
        self.action = action     # função callback
        self.hotkey = hotkey
        self.rect = None         # definido ao renderizar

    def handle_click(self, pos):
        if self.rect and self.rect.collidepoint(pos):
            self.action()
            return True
        return False


class MenuContext:
    EMPTY    = "empty"
    UNIT     = "unit"
    BUILDING = "building"


class HUDManager:
    def __init__(self, hud_sprite, grid_cols=3, grid_rows=3):
        self.sprite = hud_sprite   # seu sprite da caixa
        self.cols = grid_cols
        self.rows = grid_rows
        self.current_buttons = []
        self.menus = {}            # context_key -> list[Button]

    def register_menu(self, context_key, buttons):
        self.menus[context_key] = buttons

    def set_context(self, entity):
        """Chame isso sempre que a seleção mudar."""
        key = self._resolve_context(entity)
        self.current_buttons = self.menus.get(key, [])

    def _resolve_context(self, entity):
        if entity is None:
            return MenuContext.EMPTY
        if hasattr(entity, "train_unit"):   # é uma construção
            return MenuContext.BUILDING
        return MenuContext.UNIT

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in self.current_buttons:
                btn.handle_click(event.pos)
        if event.type == pygame.KEYDOWN:
            for btn in self.current_buttons:
                if btn.hotkey == event.key:
                    btn.action()

    def draw(self, surface):
        # distribui os botões na grade
        for i, btn in enumerate(self.current_buttons[:self.cols * self.rows]):
            col = i % self.cols
            row = i // self.cols
            x = self.sprite_rect.x + 8 + col * (BTN_W + GAP)
            y = self.sprite_rect.y + 8 + row * (BTN_H + GAP)
            btn.rect = pygame.Rect(x, y, BTN_W, BTN_H)
            surface.blit(btn.icon, btn.rect)