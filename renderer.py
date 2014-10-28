import config

render_queue = []

class Renderer:

    def __init__(self , screen, current_map):
        self.current_map = current_map
        self.screen = screen

    def render(self , render_queue):
        for item in render_queue:
            self.screen(item['image'] , item['position'])