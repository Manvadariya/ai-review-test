from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pygame


WIDTH = 900
HEIGHT = 640
PANEL_PADDING = 24
ROW_HEIGHT = 60
INPUT_HEIGHT = 54
BUTTON_WIDTH = 110
BUTTON_HEIGHT = 44
FPS = 60


@dataclass(slots=True)
class TodoItem:
    text: str
    completed: bool = False


class TodoListModel:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.items: list[TodoItem] = []
        self.selected_index = 0

    def load(self) -> None:
        if not self.storage_path.exists():
            return

        with self.storage_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        self.items = [TodoItem(**item) for item in payload]
        self.selected_index = self._clamp_selection(self.selected_index)

    def save(self) -> None:
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump([asdict(item) for item in self.items], handle, indent=2)

    def add_item(self, text: str) -> bool:
        cleaned = text.strip()
        if not cleaned:
            return False

        self.items.append(TodoItem(text=cleaned))
        self.selected_index = len(self.items) - 1
        self.save()
        return True

    def toggle_selected(self) -> bool:
        if not self.items:
            return False

        item = self.items[self.selected_index]
        item.completed = not item.completed
        self.save()
        return True

    def delete_selected(self) -> bool:
        if not self.items:
            return False

        del self.items[self.selected_index]
        self.selected_index = self._clamp_selection(self.selected_index)
        self.save()
        return True

    def move_selection(self, offset: int) -> None:
        if not self.items:
            self.selected_index = 0
            return

        self.selected_index = (self.selected_index + offset) % len(self.items)

    def click_index_for_position(self, y_pos: int, list_top: int) -> int | None:
        relative = y_pos - list_top
        if relative < 0:
            return None

        index = relative // ROW_HEIGHT
        if 0 <= index < len(self.items):
            return index
        return None

    def _clamp_selection(self, index: int) -> int:
        if not self.items:
            return 0
        return max(0, min(index, len(self.items) - 1))


class Button:
    def __init__(self, label: str, rect: pygame.Rect) -> None:
        self.label = label
        self.rect = rect

    def contains(self, position: tuple[int, int]) -> bool:
        return self.rect.collidepoint(position)


class TodoApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pygame Todo")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("georgia", 34, bold=True)
        self.body_font = pygame.font.SysFont("consolas", 22)
        self.small_font = pygame.font.SysFont("consolas", 18)
        self.model = TodoListModel(Path(__file__).with_name("todos.json"))
        self.model.load()
        self.input_text = ""
        self.running = True
        self.message = "Type a task and press Enter or click Add."
        self.buttons = self._build_buttons()

    def _build_buttons(self) -> dict[str, Button]:
        buttons_top = PANEL_PADDING + INPUT_HEIGHT + 18
        left = WIDTH - PANEL_PADDING - BUTTON_WIDTH
        gap = 12
        return {
            "add": Button("Add", pygame.Rect(left, buttons_top, BUTTON_WIDTH, BUTTON_HEIGHT)),
            "toggle": Button(
                "Toggle",
                pygame.Rect(left, buttons_top + BUTTON_HEIGHT + gap, BUTTON_WIDTH, BUTTON_HEIGHT),
            ),
            "delete": Button(
                "Delete",
                pygame.Rect(left, buttons_top + (BUTTON_HEIGHT + gap) * 2, BUTTON_WIDTH, BUTTON_HEIGHT),
            ),
        }

    def run(self) -> None:
        while self.running:
            self._handle_events()
            self._draw()
            self.clock.tick(FPS)

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.running = False
            return

        if event.key == pygame.K_RETURN:
            self._add_from_input()
            return

        if event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
            return

        if event.key == pygame.K_UP:
            self.model.move_selection(-1)
            self.message = self._selection_message()
            return

        if event.key == pygame.K_DOWN:
            self.model.move_selection(1)
            self.message = self._selection_message()
            return

        if event.key == pygame.K_SPACE:
            if self.model.toggle_selected():
                self.message = self._selection_message()
            return

        if event.key == pygame.K_DELETE:
            if self.model.delete_selected():
                self.message = "Deleted selected task."
            return

        if event.unicode.isprintable():
            self.input_text += event.unicode

    def _handle_click(self, position: tuple[int, int]) -> None:
        for name, button in self.buttons.items():
            if button.contains(position):
                if name == "add":
                    self._add_from_input()
                elif name == "toggle" and self.model.toggle_selected():
                    self.message = self._selection_message()
                elif name == "delete" and self.model.delete_selected():
                    self.message = "Deleted selected task."
                return

        list_top = PANEL_PADDING + INPUT_HEIGHT + 18
        clicked_index = self.model.click_index_for_position(position[1], list_top)
        if clicked_index is not None:
            self.model.selected_index = clicked_index
            self.message = self._selection_message()

    def _add_from_input(self) -> None:
        if self.model.add_item(self.input_text):
            self.message = f"Added: {self.input_text.strip()}"
            self.input_text = ""
        else:
            self.message = "Enter a non-empty task before adding it."

    def _selection_message(self) -> str:
        if not self.model.items:
            return "No tasks yet."

        current = self.model.items[self.model.selected_index]
        state = "done" if current.completed else "open"
        return f"Selected '{current.text}' ({state})."

    def _draw(self) -> None:
        self._draw_background()
        self._draw_header()
        self._draw_input_area()
        self._draw_buttons()
        self._draw_task_list()
        self._draw_footer()
        pygame.display.flip()

    def _draw_background(self) -> None:
        self.screen.fill((245, 238, 225))
        pygame.draw.circle(self.screen, (224, 196, 156), (150, 90), 120)
        pygame.draw.circle(self.screen, (190, 214, 205), (770, 570), 180)
        pygame.draw.rect(self.screen, (255, 250, 244), pygame.Rect(18, 18, WIDTH - 36, HEIGHT - 36), border_radius=24)

    def _draw_header(self) -> None:
        title = self.title_font.render("Todo Desk", True, (45, 44, 39))
        subtitle = self.small_font.render(
            "Enter to add, Up/Down to select, Space to toggle, Delete to remove.",
            True,
            (92, 89, 81),
        )
        self.screen.blit(title, (PANEL_PADDING, PANEL_PADDING - 4))
        self.screen.blit(subtitle, (PANEL_PADDING, PANEL_PADDING + 38))

    def _draw_input_area(self) -> None:
        input_rect = pygame.Rect(PANEL_PADDING, PANEL_PADDING + 74, WIDTH - 2 * PANEL_PADDING - BUTTON_WIDTH - 18, INPUT_HEIGHT)
        pygame.draw.rect(self.screen, (255, 255, 255), input_rect, border_radius=14)
        pygame.draw.rect(self.screen, (124, 106, 83), input_rect, width=2, border_radius=14)

        content = self.input_text or "Write the next thing that matters..."
        color = (48, 48, 45) if self.input_text else (150, 147, 139)
        rendered = self.body_font.render(content, True, color)
        self.screen.blit(rendered, (input_rect.x + 16, input_rect.y + 14))

    def _draw_buttons(self) -> None:
        for name, button in self.buttons.items():
            palette = {
                "add": ((70, 119, 94), (244, 245, 240)),
                "toggle": ((69, 92, 117), (244, 245, 240)),
                "delete": ((146, 76, 68), (244, 245, 240)),
            }[name]
            pygame.draw.rect(self.screen, palette[0], button.rect, border_radius=12)
            text = self.small_font.render(button.label, True, palette[1])
            text_rect = text.get_rect(center=button.rect.center)
            self.screen.blit(text, text_rect)

    def _draw_task_list(self) -> None:
        list_top = PANEL_PADDING + INPUT_HEIGHT + 92
        list_height = HEIGHT - list_top - 80
        panel_rect = pygame.Rect(PANEL_PADDING, list_top, WIDTH - 2 * PANEL_PADDING, list_height)
        pygame.draw.rect(self.screen, (252, 248, 241), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (207, 193, 170), panel_rect, width=2, border_radius=20)

        if not self.model.items:
            empty = self.body_font.render("No tasks yet. Add one above to get started.", True, (110, 108, 102))
            self.screen.blit(empty, (panel_rect.x + 24, panel_rect.y + 24))
            return

        for index, item in enumerate(self.model.items):
            row_rect = pygame.Rect(panel_rect.x + 14, panel_rect.y + 14 + index * ROW_HEIGHT, panel_rect.width - 28, ROW_HEIGHT - 10)
            if row_rect.bottom > panel_rect.bottom - 12:
                break

            selected = index == self.model.selected_index
            fill = (237, 226, 209) if selected else (255, 253, 249)
            border = (129, 104, 83) if selected else (219, 206, 185)
            pygame.draw.rect(self.screen, fill, row_rect, border_radius=14)
            pygame.draw.rect(self.screen, border, row_rect, width=2, border_radius=14)

            status_rect = pygame.Rect(row_rect.x + 14, row_rect.y + 14, 24, 24)
            pygame.draw.rect(self.screen, (255, 255, 255), status_rect, border_radius=6)
            pygame.draw.rect(self.screen, (96, 121, 108), status_rect, width=2, border_radius=6)
            if item.completed:
                pygame.draw.line(self.screen, (96, 121, 108), (status_rect.x + 5, status_rect.y + 13), (status_rect.x + 10, status_rect.y + 18), 3)
                pygame.draw.line(self.screen, (96, 121, 108), (status_rect.x + 10, status_rect.y + 18), (status_rect.x + 18, status_rect.y + 7), 3)

            text_color = (111, 117, 113) if item.completed else (44, 44, 42)
            text = item.text if len(item.text) <= 52 else item.text[:49] + "..."
            rendered = self.body_font.render(text, True, text_color)
            self.screen.blit(rendered, (status_rect.right + 14, row_rect.y + 12))

            state = "done" if item.completed else "open"
            state_text = self.small_font.render(state, True, (124, 120, 114))
            self.screen.blit(state_text, (row_rect.right - 58, row_rect.y + 18))

    def _draw_footer(self) -> None:
        footer = self.small_font.render(self.message, True, (82, 81, 76))
        self.screen.blit(footer, (PANEL_PADDING, HEIGHT - 44))


def main() -> None:
    TodoApp().run()


if __name__ == "__main__":
    main()